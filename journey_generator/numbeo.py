import time

import requests

from journey_generator import app, db
from models import Destinations
from random import choice
import re
from lxml import etree

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
    'Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0']


with app.app_context():
    cities = [i.as_dict() for i in Destinations.query.filter(Destinations.country_code == 'US',
                                                             Destinations.insulted == None).all()]
print len(cities)
base_url = "http://www.numbeo.com/{section}/city_result.jsp"
results = []
counter = 0

for city in cities:
    print counter
    counter += 1

    params = {"country": city['country_name'],
              "city": city['ascii_name'] + ', ' + city['state'],
              "displayCurrency": "USD"}

    ### GET COST OF LIVING DATA ###

    results = {}

    numbeo_url = base_url.format(section="travel-prices")
    response = requests.get(numbeo_url, params=params, headers={'User-Agent': choice(USER_AGENTS)})
    print response.request.url
    if "Numbeo doesn't have that city in the database." in response.content:
        print 'City not in database, skipping.'
        continue

    price_results = re.findall('= (\d+\.\d+)', response.content)
    if len(price_results) == 2:
        results['backpacker_price'] = price_results[0]
        results['normal_price'] = price_results[1]


    ### GET CRIME DATA ###
    numbeo_url = base_url.format(section="crime")
    response = requests.get(numbeo_url, params=params, headers={'User-Agent': choice(USER_AGENTS)})
    print response.request.url
    tree = etree.fromstring(response.content, etree.HTMLParser())
    try:
        crime_table, walking_crime_table = tree.xpath(
            "//table[@class='table_builder_with_value_explanation data_wide_table']")
        crime_values = re.findall('\d+\.\d+', etree.tostring(crime_table))
        walking_crime_values = re.findall('\d+\.\d+', etree.tostring(walking_crime_table))
        crime_keys = [
            "overall_crime",
            "crime_increasing_3yrs",
            "home_theft",
            "robbery",
            "car_stolen",
            "car_theft",
            "assault",
            "insulted",
            "hate_crime",
            "drugs",
            "property_crimes",
            "violent_crimes",
            "corruption_bribery",
            "walking_day",
            "walking_night"
        ]
        results.update(dict(zip(crime_keys, crime_values + walking_crime_values)))
    except (IndexError, ValueError):
        pass

    ### GET POLLUTION DATA ###
    numbeo_url = base_url.format(section="pollution")
    response = requests.get(numbeo_url, params=params, headers={'User-Agent': choice(USER_AGENTS)})
    print response.request.url
    tree = etree.fromstring(response.content, etree.HTMLParser())

    try:
        pollution_table = tree.xpath("//table[@class='table_builder_with_value_explanation data_wide_table']")[1]
        pollution_values = re.findall('\d+\.\d+', etree.tostring(pollution_table))
        pollution_keys = [
            "air_quality",
            "drinking_water_quality",
            "garbage_disposal",
            "cleanliness",
            "quiet",
            "water_quality",
            "comfortable_in_city",
            "quality_of_greenery"
        ]
        results.update(dict(zip(pollution_keys, pollution_values)))
    except IndexError:
        pass

    with app.app_context():
        if results:
            city.update(results)
            db.session.merge(Destinations(**city))
            db.session.commit()

    if counter % 50 == 0:
        time.sleep(60)
    else:
        time.sleep(2)
