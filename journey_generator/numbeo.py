import time

from geomind_data import load_geomind_data
import requests
from models import db, Countries, Destinations, Climate
from random import choice
import re
from lxml import etree

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
    'Mozilla/5.0 (compatible; MSIE 10.6; Windows NT 6.1; Trident/5.0; InfoPath.2; SLCC1; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET CLR 2.0.50727) 3gpp-gba UNTRUSTED/1.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10; rv:33.0) Gecko/20100101 Firefox/33.0']

# cities = load_geomind_data()
# countries = [i.as_dict() for i in Countries.query.all()]
cities = [i.as_dict() for i in Destinations.query.all()]
# existing_city_key = [existing_city.city_name + existing_city.country_code for existing_city in existing_cities]
# cities_key = [city['name'] + city['country_code'] for city in cities]
# remaining_cities = [city for i, city in enumerate(cities) if cities_key[i] not in existing_city_key]


# for city in cities:
#     country = [country for country in countries if country['countrycode'] == city['country_code']]
#     if country:
#         city.update(country[0])

base_url = "http://www.numbeo.com/{section}/city_result.jsp"
results = []
counter = 0

for city in cities:
    print counter
    counter += 1
    if city['country_code'] == 'US':
        continue

    params = {"country": city['country_name'],
              "city": city['ascii_name'],
              "displayCurrency": "USD"}

    # numbeo_url = base_url.format(section="travel-prices")
    # response = requests.get(numbeo_url, params=params, headers={'User-Agent': choice(USER_AGENTS)})
    # print response.request.url
    # price_results = re.findall('= (\d+\.\d+)', response.content)
    # if len(price_results) != 2:
    #     print 'No price found, skipping'
    #     continue

    # backpacker_price, normal_price = map(float, price_results)
    # print price_results

    results = {}

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

    ### GET CLIMATE DATA ###
    numbeo_url = base_url.format(section="climate")
    response = requests.get(numbeo_url, params=params, headers={'User-Agent': choice(USER_AGENTS)})
    print response.request.url
    tree = etree.fromstring(response.content, etree.HTMLParser())
    climate_data = []

    try:
        climate_table = etree.tostring(tree.xpath('//table')[-3])
        climate_values = re.findall('(\d+)&#8457;', climate_table)
        months = [
            "january",
            "febuary",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december"
        ]
        i = 0
        for month in months:
            climate_data.append({
                "city_id": city['id'],
                "month": month,
                "low_temp": climate_values[i],
                "high_temp": climate_values[i + 1]
            })
            i += 2

    except IndexError:
        pass

    if results:
        city.update(results)
        db.session.merge(Destinations(**city))
        db.session.commit()
    if climate_data:
        db.session.add_all([Climate(**climate_row) for climate_row in climate_data])
        db.session.commit()

    if counter % 50 == 0:
        time.sleep(60)
    else:
        time.sleep(2)

print 'foo'
