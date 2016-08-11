from flask_restful import Resource, Api, abort, fields, marshal_with
from journey_generator import app, db
from journey_generator.base import BaseResource
from models import Climate, Destinations

api = Api(app)


class DestinationsResource(BaseResource):
    model_class = Destinations
    model_name = "destinations"
    associated_objects = ["climate"]


api.add_resource(DestinationsResource, '/destination/<int:id>', '/destinations')

if __name__ == '__main__':
    app.run(debug=True)
