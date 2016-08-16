from flask_restful import Resource, Api, abort, fields, marshal_with
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

class DestinationsResource(BaseResource):
    model_class = Destinations
    model_name = "destinations"
    associated_objects = ["climate"]


api.add_resource(DestinationsResource, '/destination/<int:id>', '/destinations')

if __name__ == '__main__':
    app.run(debug=True)
