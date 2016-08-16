import requests
from journey_generator import db, app
from journey_generator.models import Destinations



response = requests.get('https://nomadlist.com/api/v2/list/cities')
response_results = response.json()['result']
results = []

for result in response_results:
    result_dict = {}
    result_dict['ascii_name'] = result['info']['city']['name'].encode('utf-8')
    result_dict['country_name'] = result['info']['country']['name']

    scores = result['scores']

    result_dict['life_score'] = scores['life_score']
    result_dict['nightlife_score'] = scores['nightlife']
    result_dict['leisure_score'] = scores['leisure']
    result_dict['safety_score'] = scores['safety']
    result_dict['friendly_to_foreigners_score'] = scores['friendly_to_foreigners']
    result_dict['racism_score'] = scores['racism']
    result_dict['lgbt_friendly_score'] = scores['lgbt_friendly']
    result_dict['female_friendly_score'] = scores['female_friendly']

    result_dict['tags'] = result['tags']

    results.append(result_dict)

with app.app_context():
    for result in results:
            print 'Searching for match for {} - {}'.format(result['ascii_name'], result['country_name'])
            matched_destination = db.session.query(Destinations).filter(Destinations.ascii_name == result['ascii_name'],
                                                  Destinations.country_name == result['country_name']).first()
            if matched_destination:
                print 'Match found! Committing...'
                matched_destination.from_dict(result)
                db.session.commit()
            else:
                print 'No match found :('
