import requests
import time

from journey_generator import app, db
from journey_generator.models import Destinations
from journey_generator.settings import GOOGLE_CUSTOM_SEARCH_ID, GOOGLE_API_KEY

base_url = "https://www.googleapis.com/customsearch/v1"


with app.app_context():
    destinations = Destinations.query.filter(Destinations.tripadvisor_link == None).all()

    results = []
    counter = 0
    for destination in destinations:
        params = {
            "cx": GOOGLE_CUSTOM_SEARCH_ID,
            "key": GOOGLE_API_KEY,
            "q": destination.ascii_name + " " + destination.country_name
        }
        try:
            resp = requests.get(base_url, params=params)
            if not resp.ok:
                time.sleep(3)
                resp = requests.get(base_url, params=params)
            print str(counter) + ": " + resp.request.url
            counter += 1
            links = [item['link'] for item in resp.json()['items']]
            for link in links:
                if link.startswith("https://www.tripadvisor.com/Tourism-g"):
                    print "Found match: " + link
                    destination.tripadvisor_link = link
                    db.session.commit()
                    break
        except:
            raise
