from datetime import date, datetime

from flask_restful import Resource, Api, abort, fields, marshal_with, reqparse
from sqlalchemy import asc, desc, or_
from sqlalchemy.dialects import postgresql

from journey_generator import app, db
from journey_generator.base import BaseResource
from journey_generator.settings import api_fields
from models import Climate, Destinations

api = Api(app)

if app.config['DEBUG']:
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


def create_parser(api_fields):
    parser = reqparse.RequestParser()
    for api_field in api_fields:
        parser.add_argument(api_field['api_name'],
                            type=api_field['type'],
                            default=api_field['default'],
                            dest=api_field['name'],
                            action=api_field['action'])

    return parser


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
    location_fields = ["country_code", "id", "continent_name"]
    location_filters = []
    filters = []

    for field, op_values in args.items():
        # model = get_model(field)
        # location fields are treated differently because the op_values are comma separated and they need to be
        # combined into an OR statement. {"country": "in;US,CA,GB"}
        if field in location_fields:
            operator, values_str = op_values.split(";")
            location_values = (values_str).split(',')
            model_field = getattr(Destinations, field)
            location_filter = getattr(model_field, operator_map[operator])
            location_filters.append(location_filter(location_values))

        # sort_by is treated differently because it doesn't need an operator and is parsed differently.
        elif field == "sort_by":
            sort_by_field, direction = op_values.split('.')
            try:
                model_field = getattr(Destinations, sort_by_field)
            except AttributeError:
                model_field = getattr(Climate, sort_by_field)
            sort_by_expression = getattr(model_field, direction)
        else:
            # all other fields have action="append" which means even single values are lists
            for op_value in op_values:
                operator, value = op_value.split(";")
                try:
                    value = float(value)
                except ValueError:
                    pass
                try:
                    model_field = getattr(Destinations, field)
                except AttributeError:
                    model_field = getattr(Climate, field)
                filter_expression = getattr(model_field, operator_map[operator])
                filters.append(filter_expression(value))

    query_columns = generate_columns_query(api_fields)
    destinations_query = db.session.query(*query_columns).filter(*filters).order_by(
        sort_by_expression()).filter(Climate.city_id == Destinations.id)
    if location_fields:
        destinations_query = destinations_query.filter(or_(*location_filters))

    return destinations_query


def generate_columns_query(api_fields):
    query_columns = []
    for api_field in api_fields:
        if api_field['name']:
            field = api_field['name']
            alias = api_field['api_name']
            # let's me get hybrid attributes
            try:
                column = getattr(Destinations, field)
            except AttributeError:
                column = getattr(Climate, field)
            aliased_column = getattr(column, "label")(alias)
            query_columns.append(aliased_column)
    return query_columns


class DestinationsResource(Resource):
    destinations_parser = create_parser(api_fields)

    def get(self):
        args = dict(self.destinations_parser.parse_args())
        filtered_query = convert_args_to_query(args)

        results = []
        for row in filtered_query.limit(30).all():
            results.append(row._asdict())

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
                locations_list.append({"label": location.country_name, "value": "country_code." +
                                                                                location.country_code})
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
    app.run(threaded=True)
