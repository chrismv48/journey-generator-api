import requests
import sys

from journey_generator import app, db
from models import Destinations

PLACES_API_KEY = 'AIzaSyAVoj0jf6FFrW0bt3oY6wIAEomi9Zfn6aU'

place_types = [
    'amusement_park',
    'aquarium',
    'art_gallery',
    'bar',
    'cafe',
    'clothing_store',
    'department_store',
    'jewelry_store',
    'lodging',
    'museum',
    'night_club',
    'park',
    'restaurant',
    'shopping_mall',
    'spa',
    'stadium',
    'zoo'
]
high_volume_place_types = [
    "bar",
    "cafe",
    "restaurant"
]
base_url = """https://maps.googleapis.com/maps/api/place/radarsearch/json?location={location}&radius={radius}&type={place_type}&key={api_key}"""


def main():
    with app.app_context():
        destinations = Destinations.query.filter(Destinations.restaurant < 1,
                                                 Destinations.safety_score != None).all()
        counter = 0
        for destination in destinations:
            results = []
            counter += 1
            for place_type in place_types:
                radius = 5000 if place_type not in high_volume_place_types else 2000
                print 'Querying data for {}, {} - {} ({} of {})'.format(destination.ascii_name,
                                                                        destination.country_code,
                                                                        place_type,
                                                                        counter,
                                                                        len(destinations))
                request_url = base_url.format(
                    location=str(destination.latitude) + ',' + str(destination.longitude),
                    radius=radius,
                    place_type=place_type,
                    api_key=PLACES_API_KEY
                )

                resp = requests.get(request_url)
                api_results = resp.json().get('results')
                print "{} results: {}".format(len(api_results), resp.url)
                if resp.json().get('error_message'):
                    print "Error occurred: {}".format(resp.json().get('error_message'))
                    sys.exit()
                if api_results:
                    while True:
                        if len(api_results) > 197:
                            radius = int(radius * 0.7)
                            request_url = base_url.format(
                                location=str(destination.latitude) + ',' + str(destination.longitude),
                                radius=radius,
                                place_type=place_type,
                                api_key=PLACES_API_KEY
                            )
                            resp = requests.get(request_url)
                            if resp.json().get('error_message'):
                                print "Error occurred: {}".format(resp.json().get('error_message'))
                            api_results = resp.json().get('results')
                            print "{} results: {}".format(len(api_results), resp.url)
                        else:
                            break

                    setattr(destination, place_type, float(radius) / len(api_results) if len(api_results) else None)
                    results.append(destination)

            for result in results:
                db.session.merge(result)
            db.session.commit()


main()
