import math
import pandas as pd

from journey_generator import db, app
from models import Destinations
from labelizer import labelize


def normalize_column(value, min, max, subtract_from_one=True):
    if subtract_from_one:
        return 1 - ((float(value) - min) / (max - min))
    else:
        return ((float(value) - min) / (max - min))


def calculate_index(row, weights):
    return sum(row[weights.keys()] * weights.values())


environment_weights = {
    "air_quality": 0.1,
    "drinking_water_quality": 0.05,
    "garbage_disposal": 0.05,
    "cleanliness": 0.2,
    "quiet": 0.05,
    "water_quality": 0.05,
    "comfortable_in_city": 0.3,
    "quality_of_greenery": 0.2
}

with app.app_context():
    destinations = [i.as_dict() for i in Destinations.query.all()]
    df = pd.DataFrame(destinations)
    df['environment_score'] = df.apply(lambda x: calculate_index(x, environment_weights), axis=1) / 100
    df['environment_score'] = df['environment_score'].apply(lambda x: normalize_column(x,
                                                                                       df['environment_score'].min(),
                                                                                       df['environment_score'].max(),
                                                                                       subtract_from_one=False))
    df['environment_score_label'] = labelize(df['environment_score'])
    counter = 0
    for row in df.to_dict('records'):
        print counter
        db.session.merge(Destinations(**row))
        counter += 1
    db.session.commit()
