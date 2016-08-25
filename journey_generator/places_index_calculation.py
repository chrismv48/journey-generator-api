import math
import pandas as pd

from journey_generator import db, app
from models import Destinations

place_types = {
    'amusement_park': ('attractions_score', 0.2),
    'aquarium': ('attractions_score', 0.25),
    'stadium': ('attractions_score', 0.1),
    'park': ('attractions_score', 0.2),
    'zoo': ('attractions_score', 0.25),
    'bar': ('nightlife_score', 0.35),
    'night_club': ('nightlife_score', 0.65),
    'clothing_store': ('shopping_score', 0.2),
    'department_store': ('shopping_score', 0.3),
    'shopping_mall': ('shopping_score', 0.3),
    'jewelry_store': ('shopping_score', 0.2),
    'art_gallery': ('culture_score', 0.4),
    'museum': ('culture_score', 0.6),
    'cafe': ('dining_score', 0.35),
    'restaurant': ('dining_score', 0.65),
    'lodging': ('lodging_score', 1),
    'spa': ('spas_score', 1)
}

meta_place_weights = {
    "attractions_score": 0.2,
    "culture_score": 0.2,
    "dining_score": 0.2,
    "nightlife_score": 0.15,
    "shopping_score": 0.1,
    "lodging_score": 0.1,
    "spas_score": 0.05
}


# assert sum(meta_place_weights.values()) == 1

def normalize_column(value, min, max, subtract_from_one=True):
    if subtract_from_one:
        return 1 - ((float(value) - min) / (max - min))
    else:
        return ((float(value) - min) / (max - min))


def transform_invert(value, max):
    return math.log(1 + (max / value if value else 0))


def calculate_places_index(row, weights):
    return sum(row[weights.keys()] * weights.values())


with app.app_context():
    destinations = [i.as_dict() for i in Destinations.query.all()]

    df = pd.DataFrame(destinations)
    df = df.fillna(0)
    meta_place_scores = {}

    for place_type in place_types.keys():
        transformed = df[place_type].apply(lambda x: transform_invert(x, df[place_type].max()))
        df[place_type + '_index'] = transformed.apply(lambda x: normalize_column(x,
                                                                                 transformed.min(),
                                                                                 transformed.max(),
                                                                                 subtract_from_one=False))
        place_type_quantiles = df[place_type + '_index'][df[place_type + '_index'] > 0].quantile([0.3, 0.5, 0.7,
                                                                                                  0.9]).tolist()
        place_type_quantiles.insert(0, 0)
        place_type_quantiles.append(1)

        # check if there are duplicate quantiles. This can happen if data is has a lot of duplicate values due to
        # sparsity in variety (zoo's).
        if len(place_type_quantiles) != len(set(place_type_quantiles)):
            duplicate_indexes = [i for i, n in enumerate(place_type_quantiles) if place_type_quantiles.count(n) > 1]
            for i, n in enumerate(duplicate_indexes):
                place_type_quantiles[n] = place_type_quantiles[n] + (0.001 * i)
        labels = range(1, 6)
        df[place_type + '_label'] = pd.cut(df[place_type + '_index'], bins=place_type_quantiles, labels=labels,
                                           include_lowest=True)
        ### do meta place stuff ###


        meta_place_type, weight = place_types[place_type]
        df[meta_place_type] = df.get(meta_place_type, 0) + (df[place_type + '_index'] * weight)

    for meta_place_type in set([v[0] for v in place_types.values()]):
        df[meta_place_type] = df[meta_place_type].apply(lambda x: normalize_column(x,
                                                                                   df[meta_place_type].min(),
                                                                                   df[meta_place_type].max(),
                                                                                   subtract_from_one=False))
        meta_place_type_quantiles = df[meta_place_type][df[meta_place_type] > 0].quantile([0.3, 0.5, 0.7,
                                                                                           0.9]).tolist()
        meta_place_type_quantiles.insert(0, 0)
        meta_place_type_quantiles.append(1)
        # check if there are duplicate quantiles. This can happen if data is has a lot of duplicate values due to
        # sparsity in variety (zoo's).
        if len(meta_place_type_quantiles) != len(set(meta_place_type_quantiles)):
            duplicate_indexes = [i for i, n in enumerate(meta_place_type_quantiles) if
                                 meta_place_type_quantiles.count(n) > 1]
            for i, n in enumerate(duplicate_indexes):
                meta_place_type_quantiles[n] = meta_place_type_quantiles[n] + (0.001 * i)
        labels = range(1, 6)
        df[meta_place_type + '_label'] = pd.cut(df[meta_place_type], bins=meta_place_type_quantiles, labels=labels,
                                                include_lowest=True)

    df['places_index'] = df.apply(lambda rows: calculate_places_index(rows, meta_place_weights), axis=1)

    df['places_index'] = df['places_index'].apply(lambda x: normalize_column(x,
                                                                             df['places_index'].min(),
                                                                             df['places_index'].max(),
                                                                             subtract_from_one=False))

    place_index_quantiles = df['places_index'][df['places_index'] > 0].quantile([0.3, 0.5, 0.7,
                                                                                 0.9]).tolist()
    place_index_quantiles.insert(0, 0)
    place_index_quantiles.append(1)
    if len(place_index_quantiles) != len(set(place_index_quantiles)):
        duplicate_indexes = [i for i, n in enumerate(place_index_quantiles) if
                             place_index_quantiles.count(n) > 1]
        for i, n in enumerate(duplicate_indexes):
            place_index_quantiles[n] = place_index_quantiles[n] + (0.001 * i)
    labels = range(1, 6)
    df['places_index_label'] = pd.cut(df['places_index'], bins=place_index_quantiles, labels=labels,
                                      include_lowest=True)
    df.tags[df.tags == 0] = None
    for row in df.to_dict('records'):
        db.session.merge(Destinations(**row))

    db.session.commit()
