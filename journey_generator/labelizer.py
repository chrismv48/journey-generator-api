import pandas as pd

from journey_generator import app, db
from journey_generator.models import Destinations, Climate


def normalize_column(value, min, max, subtract_from_one=True):
    if subtract_from_one:
        return 1 - ((float(value) - min) / (max - min))
    else:
        return ((float(value) - min) / (max - min))


def labelize(series, quantile_values=None, labels=None):
    if not quantile_values:
        quantile_values = [0.3, 0.5, 0.7, 0.9]
    if not labels:
        labels = range(1, 6)

    quantiles = series.quantile(quantile_values).tolist()
    quantiles.insert(0, 0)
    quantiles.append(1)

    if len(quantiles) != len(set(quantiles)):
        duplicate_indexes = [i for i, n in enumerate(quantiles) if quantiles.count(n) > 1]
        for i, n in enumerate(duplicate_indexes):
            quantiles[n] = quantiles[n] + (0.001 * i)

    labeled_series = pd.cut(series, bins=quantiles, labels=labels, include_lowest=True)

    return labeled_series


with app.app_context():
    # destinations = [i.as_dict() for i in Destinations.query.filter(Destinations.insulted != None).all()]
    climates = [i.as_dict() for i in Climate.query.filter(Climate.weather_index != None).all()]

    df = pd.DataFrame(climates)
    df['weather_index_label'] = labelize(df['weather_index'])
    # df['safety_score_label'] = labelize(df['safety_score'])
    # normalized_population = df['population'].apply(lambda x: normalize_column(x,
    #                                                                           df['population'].min(),
    #                                                                           df['population'].max(),
    #                                                                           subtract_from_one=False))
    # df['we'] = labelize(normalized_population)

    counter = 0
    for row in df.to_dict('records'):
        print counter
        db.session.merge(Climate(**row))
        counter += 1
    db.session.commit()
