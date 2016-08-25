from datetime import date

from flask_restful import Resource, Api, abort, fields, marshal_with, reqparse
from sqlalchemy import asc, desc

from journey_generator import app, db
from journey_generator.base import BaseResource
from models import Climate, Destinations

api = Api(app)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')

    return response


def is_month(value, name):
    if value in ['january',
                 'february',
                 'march',
                 'april',
                 'may',
                 'june',
                 'july',
                 'august',
                 'september',
                 'october',
                 'november',
                 'december']:
        return value
    else:
        raise ValueError("Invalid month. Ensure you use the full unabbreviated month in all lower case.")


destinations_parser = reqparse.RequestParser()
destinations_parser.add_argument('month', type=is_month)
destinations_parser.add_argument('continents', type=str)
destinations_parser.add_argument('sort_by', type=str)
destinations_parser.add_argument('countries', type=str)
destinations_parser.add_argument('population_gte', type=int)
destinations_parser.add_argument('population_lte', type=int)
destinations_parser.add_argument('safety_score_gte', type=float)
destinations_parser.add_argument('weather_index_gte', type=float)


class DestinationsResource(Resource):
    def get(self):
        args = dict(destinations_parser.parse_args())
        month = args.get('month') or date.today().strftime('%B').lower()
        continents = args.get('continents').split(',') if args.get('continents') else None
        countries = args.get('countries').split(',') if args.get('countries') else None
        sort_by, direction = args.get('sort_by').split('.') if args.get('sort_by') else ('weather_index','desc')
        population_gte = args.get('population_gte')
        population_lte = args.get('population_lte')
        safety_score_gte = args.get('safety_score_gte')
        weather_index_gte = args.get('weather_index_gte')

        destinations_query = db.session.query(Destinations, Climate).join(Climate).filter(
            Destinations.safety_score != None,
            Climate.month == month).order_by(sort_by + " " + direction)
        if continents:
            destinations_query = destinations_query.filter(Destinations.continent_name.in_(continents))
        if countries:
            destinations_query = destinations_query.filter(Destinations.country_name.in_(countries))
        if population_gte:
            destinations_query = destinations_query.filter(Destinations.population >= population_gte)
        if population_lte:
            destinations_query = destinations_query.filter(Destinations.population <= population_lte)
        if safety_score_gte:
            destinations_query = destinations_query.filter(Destinations.safety_score >= safety_score_gte)
        if weather_index_gte:
            destinations_query = destinations_query.filter(Climate.weather_index >= weather_index_gte)

        results = []
        for destination, climate in destinations_query.limit(100).all():
            row_dict = destination.as_dict()
            row_dict.update(climate.as_dict())
            results.append(row_dict)

        return {"destinations": results}


class DestinationResource(Resource):
    pass


api.add_resource(DestinationsResource, '/destinations')
api.add_resource(DestinationResource, '/destination/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)
