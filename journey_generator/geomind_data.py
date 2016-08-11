import unicodecsv

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
    "population",
    "timezone",
    "modification_date"
]

def load_geomind_data():

    with open('cities5000.txt', 'rb') as f:
        reader = unicodecsv.DictReader(f, fieldnames=headers, quoting=unicodecsv.QUOTE_NONE, delimiter='\t')
        cities = []
        for row in reader:
            cities.append({k:v for k, v in row.iteritems() if k in desired_fields})

    return cities

# with open('cities5000.csv', 'wb') as f:
#     writer = unicodecsv.DictWriter(f, fieldnames=desired_fields, quoting=unicodecsv.QUOTE_ALL, delimiter='\t')
#     writer.writeheader()
#     writer.writerows(cities)
