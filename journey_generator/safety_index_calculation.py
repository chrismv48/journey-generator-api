import pandas as pd

from journey_generator import app, db
from journey_generator.models import Destinations

with app.app_context():
    destinations = [i.as_dict() for i in Destinations.query.filter(Destinations.insulted != None).all()]

    df = pd.DataFrame(destinations)

    # nomdalist_safety_score_weights = {
    #     "safety_score": .5,
    #     "friendly_to_foreigners_score": 0.125,
    #     "racism_score": 0.125,
    #     "lgbt_friendly_score": 0.125,
    #     "female_friendly_score": 0.125
    # }
    # assert sum(nomdalist_safety_score_weights.values()) == 1


    # def calculate_nomadlist_safety_score(row, weights):
    #     scores = row[weights.keys()].to_dict()
    #     filtered_scores = {k: v for k, v in scores.items() if v}
    #     new_weights = {k: v for k, v in weights.items() if k in filtered_scores.keys()}
    #     new_weights = {k: v + (v * (sum(weights.values()) - sum(new_weights.values()))) for k, v in new_weights.items()}
    #     return sum([v * new_weights[k] for k, v in filtered_scores.items()])
    #
    #
    # df['nomadlist_safety_score'] = df.apply(lambda x: calculate_nomadlist_safety_score(x,
    #                                                                                    nomdalist_safety_score_weights),
    #                                         axis=1)
    numbeo_safety_score_weights = {
        "home_theft": 0.1,
        "robbery": 0.1,
        "car_stolen": 0.05,
        "car_theft": 0.05,
        "assault": 0.2,
        "insulted": 0.1,
        "hate_crime": 0.1,
        "drugs": 0.05,
        "property_crimes": 0.05,
        "violent_crimes": 0.2
    }


    def calculate_numbeo_safety_score(row, weights):
        return sum(row[weights.keys()] * weights.values())


    df['safety_score'] = df.apply(lambda x: calculate_numbeo_safety_score(x, numbeo_safety_score_weights),
                                         axis=1) / 100

    # df['composite_safety_score'] = df['numbeo_safety_score'] * .5 + df['nomadlist_safety_score'] * .5

    counter = 0
    for row in df.to_dict('records'):
        print counter
        db.session.merge(Destinations(**row))
        counter += 1
    db.session.commit()
