import pandas as pd

from journey_generator import app, db
from journey_generator.models import Climate

with app.app_context():
    climate_data = [i.as_dict() for i in Climate.query.filter(Climate.cloud_cover != None).all()]

df = pd.DataFrame(climate_data)

### Calculate Temperature Index ###
IDEAL_MIN_TEMP = 65
IDEAL_MAX_TEMP = 77


def variance_from_ideal_temp_range(row):
    # penalize hotter climates more by multiplying by 2
    return abs(IDEAL_MIN_TEMP - row['apparent_low_temp']) + (abs(IDEAL_MAX_TEMP - row['apparent_high_temp']) * 2)


def normalize_column(value, min, max):
    return 1 - ((float(value) - min) / (max - min))


temp_variance = df.apply(variance_from_ideal_temp_range, axis=1)
df['temp_index'] = temp_variance.apply(lambda x: normalize_column(x,
                                                                  temp_variance.min(),
                                                                  temp_variance.max()))

### Calculate Humidity Index ###
IDEAL_MIN_HUMIDITY = .40
IDEAL_MAX_HUMIDITY = .50


def variance_from_ideal_range(value, min, max):
    if value > max:
        return value - max
    elif value < min:
        return min - value
    else:
        return 0


humidity_variance = df.humidity.apply(lambda x: variance_from_ideal_range(x,
                                                                          IDEAL_MIN_HUMIDITY,
                                                                          IDEAL_MAX_HUMIDITY))
df['humidity_index'] = humidity_variance.apply(lambda x: normalize_column(x,
                                                                          humidity_variance.min(),
                                                                          humidity_variance.max()))

### Calculate Wind Speed Index ###
IDEAL_MIN_WIND_SPEED = 2.5
IDEAL_MAX_WIND_SPEED = 4.5

wind_speed_variance = df.wind_speed.apply(lambda x: variance_from_ideal_range(x,
                                                                              IDEAL_MIN_WIND_SPEED,
                                                                              IDEAL_MAX_WIND_SPEED))
df['wind_speed_index'] = wind_speed_variance.apply(lambda x: normalize_column(x,
                                                                              wind_speed_variance.min(),
                                                                              wind_speed_variance.max()))

### Calculate Rainfall Index ###
df['rain_probability_index'] = df.rain_probability.apply(lambda x: normalize_column(x,
                                                                                    df.rain_probability.min(),
                                                                                    df.rain_probability.max()))

### Calculate Cloud Cover Index ###
df['cloud_cover_index'] = df.cloud_cover.apply(lambda x: normalize_column(x,
                                                                          df.cloud_cover.min(),
                                                                          df.cloud_cover.max()))
### Calculate Weather Index ###
weather_weights = {
    "temp_index": 0.35,
    # "humidity_index": 0.2,
    "wind_speed_index": 0.15,
    "rain_probability_index": 0.3,
    "cloud_cover_index": 0.20
}

assert sum(weather_weights.values()) == 1


def calculate_weather_index(row, weights):
    return sum(row[weights.keys()] * weights.values())


df['weather_index'] = df.apply(lambda row: calculate_weather_index(row, weather_weights), axis=1)
df['weather_index'] = 1 - df['weather_index'].apply(lambda x: normalize_column(x,
                                                                               df['weather_index'].min(),
                                                                               df['weather_index'].max()))

with app.app_context():
    counter = 0
    for row in df.to_dict('records'):
        print counter
        db.session.merge(Climate(**row))
        counter += 1
    db.session.commit()
