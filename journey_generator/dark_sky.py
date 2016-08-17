from datetime import datetime, timedelta
import pandas as pd
import requests

from settings import DARK_SKY_API_KEY
from journey_generator import app, db
from models import Destinations, Climate

DARK_SKY_URL = "https://api.forecast.io/forecast/" + DARK_SKY_API_KEY + "/{latitude},{longitude},{time}"

params = {'exclude': 'currently,minutely,hourly,alerts,flags'}
headers = {'Accept-Encoding': 'gzip'}
day_interval = 5

# TIME STRING FORMAT [YYYY]-[MM]-[DD]T[HH]:[MM]:[SS]

with app.app_context():
    destinations = db.session.query(Destinations).filter(Destinations.safety_score != None).all()
    base = datetime.now()
    times = [base - timedelta(days=x) for x in range(0, 360 * 5, day_interval)]

    for destination in destinations:
        results = []
        print 'Querying data for {} - {}'.format(destination.ascii_name, destination.country_code)
        for query_time in times:

            request_url = DARK_SKY_URL.format(latitude=destination.latitude,
                                              longitude=destination.longitude,
                                              time=query_time.strftime('%Y-%m-%dT%H:%M:%S'))
            response = requests.get(request_url, params=params, headers=headers)
            print response.request.url
            daily_data = response.json().get('daily', {}).get('data')

            if not daily_data:
                print 'No data found :('
                continue
            daily_data = daily_data[0]
            result_dict = {}
            result_dict['city_id'] = destination.id
            result_dict['month'] = query_time.strftime('%B').lower()
            result_dict['apparent_low_temp'] = daily_data.get('apparentTemperatureMin', 0)
            result_dict['low_temp'] = daily_data.get('temperatureMin', 0)
            result_dict['apparent_high_temp'] = daily_data.get('apparentTemperatureMax', 0)
            result_dict['high_temp'] = daily_data.get('temperatureMax', 0)
            result_dict['cloud_cover'] = daily_data.get('cloudCover', 0)
            result_dict['humidity'] = daily_data.get('humidity', 0)
            result_dict['dew_point'] = daily_data.get('dewPoint', 0)
            result_dict['wind_speed'] = daily_data.get('windSpeed', 0)
            result_dict['rain_probability'] = daily_data.get('precipProbability') if daily_data.get('precipType') \
                                                                                       == 'rain' else 0
            results.append(result_dict)

        df = pd.DataFrame(results)
        averaged_results = df.groupby(['city_id','month']).mean().reset_index().to_dict('records')

        db.session.add_all([Climate(**row) for row in averaged_results])
        db.session.commit()
        # for row in averaged_results:
        #     result = db.session.query(Climate).filter(Climate.city_id == row['city_id'],
        #                                      Climate.month == row['month']).first()
        #     if result:
        #         print 'Existing row found, updating...'
        #         row.pop('high_temp')
        #         row.pop('low_temp')
        #         result.from_dict(row)
        #     else:
        #         print 'No existing row found, adding new row...'
        #         db.session.add(Climate(**row))
        #     db.session.commit()
