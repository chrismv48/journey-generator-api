from datetime import date

from flask_restful import Resource, Api, abort, fields, marshal_with, reqparse
from sqlalchemy import asc, desc, or_
from sqlalchemy.dialects import postgresql

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
destinations_parser.add_argument('sort_by', type=str)
destinations_parser.add_argument('city_id', type=str, dest='id')
destinations_parser.add_argument('country', type=str, dest='country_code')
destinations_parser.add_argument('continent', type=str, dest='continent_name')
destinations_parser.add_argument('population', type=str, action='append')
destinations_parser.add_argument('safety_score', type=str, action='append')
destinations_parser.add_argument('weather_index', type=str, action='append')

def print_query(query, dialect=postgresql):
    print str(query.statement.compile(dialect=postgresql.dialect()))

def get_model(field):
    for model in [Destinations, Climate]:
        if field in model().table_fields:
            return model


operator_map = {
    "eq": "__eq__",
    "lt": "__lt__",
    "lte": "__le__",
    "gt": "__gt__",
    "gte": "__ge__",
    "in": "in_"
}


def convert_args_to_query(args):
    # Flask Restful annoyingly keeps keys with empty values
    args = {k: v for k, v in args.items() if v}

    month = args.pop('month', None) or date.today().strftime('%B').lower()

    sort_by, direction = args.pop('sort_by', None).split('.') if args.get('sort_by') else ('weather_index', 'desc')
    sort_by_expression = getattr(getattr(get_model(sort_by), sort_by), direction)

    locations = {}
    locations["country_code"] = args.pop('country_code', None)
    locations["continent_name"] = args.pop('continent_name', None)
    locations["id"] = args.pop('id', None)

    # base query will always have a sort by clause and month filter
    destinations_query = db.session.query(Destinations, Climate).join(Climate).filter(
        Climate.month == month).order_by(sort_by_expression())

    if any(locations.values()):
        or_filters = []
        for field, op_value in locations.items():
            if op_value:
                operator, value_str = op_value.split(";")
                values = (value_str).split(',')
                model_field = getattr(Destinations, field)
                or_filter = getattr(model_field, operator_map[operator])
                or_filters.append(or_filter(values))

        destinations_query = destinations_query.filter(or_(*or_filters))

    filters = []
    for field, op_values in args.items():
        model = get_model(field)
        for op_value in op_values:
            operator, value = op_value.split(";")
            model_field = getattr(model, field)
            filter_expression = getattr(model_field, operator_map[operator])
            filters.append(filter_expression(value))

    destinations_query = destinations_query.filter(*filters)

    return destinations_query


class DestinationsResource(Resource):
    def get(self):
        args = dict(destinations_parser.parse_args())
        filtered_query = convert_args_to_query(args)

        results = []
        for destination, climate in filtered_query.limit(30).all():
            row_dict = destination.as_dict()
            row_dict.update(climate.as_dict())
            results.append(row_dict)

        return {"destinations": results}


class DestinationResource(Resource):
    pass


class LocationsResource(Resource):
    def get(self):
        locations = Destinations.query.with_entities(Destinations.country_name,
                                                     Destinations.country_code,
                                                     Destinations.id,
                                                     Destinations.ascii_name,
                                                     Destinations.state,
                                                     Destinations.continent_name).all()

        locations_list = []
        countries = []
        continents = []
        for location in locations:
            city_label = ", ".join([i for i in [location.ascii_name, location.state, location.country_name] if i])
            locations_list.append({"label": city_label, "value": "city_id." + str(location.id)})
            if location.country_code not in countries:
                locations_list.append({"label": location.country_name, "value": "country." + location.country_code})
                countries.append(location.country_code)
            if location.continent_name not in continents:
                locations_list.append({"label": location.continent_name, "value":
                    "continent." + location.continent_name})
                continents.append(location.continent_name)

        return {"locations": locations_list}


api.add_resource(DestinationsResource, '/destinations')
api.add_resource(DestinationResource, '/destination/<int:id>')
api.add_resource(LocationsResource, '/locations')

if __name__ == '__main__':
    app.run(debug=True)
