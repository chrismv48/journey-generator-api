import unicodecsv
from journey_generator import app, db
from models import Destinations, GeoMindCities

headers = [
    "geoname_id",
    "name",
    "ascii_name",
    "alternate_name",
    "latitude",
    "longitude",
    "feature_class",
    "feature_code",
    "country_code",
    "cc2",
    "admin1_code",
    "admin2_code",
    "admin3_code",
    "admin4_code",
    "population",
    "elevation",
    "dem",
    "timezone",
    "modification_date"
]

desired_fields = [
    "name",
    'ascii_name',
    "latitude",
    "longitude",
    "country_code",
    "admin1_code",  # state
    "population",
    "timezone",
    "modification_date"
]

def load_geomind_data():

    with open('cities5000.txt', 'rb') as f:
        reader = unicodecsv.DictReader(f, fieldnames=headers, quoting=unicodecsv.QUOTE_NONE, delimiter='\t')
        cities = []
        for row in reader:
            # if row['country_code'] == 'US' and int(row['population']) > 25000:
            cities.append({k:v for k, v in row.iteritems() if k in desired_fields})

    return cities

# with open('cities5000.csv', 'wb') as f:
#     writer = unicodecsv.DictWriter(f, fieldnames=desired_fields, quoting=unicodecsv.QUOTE_ALL, delimiter='\t')
#     writer.writeheader()
#     writer.writerows(cities)

geomind_data = load_geomind_data()
with app.app_context():
    for row in geomind_data:
        row['city_name'] = row.pop('name')
        row['state'] = row.pop('admin1_code')
        row['geomind_modification_date'] = row.pop('modification_date')
        db.session.add(GeoMindCities(**row))
    db.session.commit()
