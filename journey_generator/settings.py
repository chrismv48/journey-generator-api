from datetime import date
import socket

DEBUG = socket.gethostname() == 'carmstrong'

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://carmstrong:Dockside6@104.131.106.228:5432/journey_generator'
SQLALCHEMY_TRACK_MODIFICATIONS = False

DARK_SKY_API_KEY = '7ae0a164364f2b21edef14fe7beca649'
GOOGLE_CUSTOM_SEARCH_ID = "011829237068144604737:dslw-th29yq"
GOOGLE_API_KEY = "AIzaSyAVoj0jf6FFrW0bt3oY6wIAEomi9Zfn6aU"

api_fields = [
    {
        "name": "ascii_name",
        "api_name": "city_name",
        "type": str,
        "default": None,
        "action": None
    },
    {
        "name": "state",
        "api_name": "us_state",
        "type": str,
        "default": None,
        "action": None
    },
    {
        "name": "country_name",
        "api_name": "country_name",
        "type": str,
        "default": None,
        "action": None
    },
    {
        "name": "month",
        "api_name": "month",
        "type": str,
        "default": lambda: ["eq;" + date.today().strftime('%B').lower()],
        "action": "append"
    },
    {
        "name": None,
        "api_name": "sort_by",
        "type": str,
        "default": 'weather_index.desc',
        "action": None
    },
    {
        "name": "id",
        "api_name": "city_id",
        "type": str,
        "default": None,
        "action": None
    },
    {
        "name": "country_code",
        "api_name": "country_code",
        "type": str,
        "default": None,
        "action": None
    },
    {
        "name": "continent_name",
        "api_name": "continent",
        "type": str,
        "default": None,
        "action": None
    },
    {
        "name": "population",
        "api_name": "population",
        "type": str,
        "default": None,
        "action": "append"
    },
    {
        "name": "population_label",
        "api_name": "population_label",
        "type": str,
        "default": None,
        "action": "append"
    },
    {
        "name": "safety_score",
        "api_name": "safety_score",
        "type": str,
        "default": None,
        "action": "append"
    },
    {
        "name": "safety_score_label",
        "api_name": "safety_score_label",
        "type": str,
        "default": None,
        "action": "append"
    },
    {
        "name": "apparent_low_temp",
        "api_name": "low_temp",
        "type": str,
        "default": None,
        "action": "append"
    },
    {
        "name": "apparent_high_temp",
        "api_name": "high_temp",
        "type": str,
        "default": None,
        "action": "append"
    },
    {
        "name": "weather_index",
        "api_name": "weather_index",
        "type": str,
        "default": None,
        "action": "append"
    },
    {
        "name": "weather_index_label",
        "api_name": "weather_index_label",
        "type": str,
        "default": None,
        "action": "append"
    },
    {
        "name": "environment_score_label",
        "api_name": "environment_score_label",
        "type": str,
        "default": None,
        "action": "append"
    },
    {
        "name": "attractions_score_label",
        "api_name": "attractions_score",
        "type": str,
        "default": None,
        "action": "append"
    },
    {
        "name": "nightlife_score_label",
        "api_name": "nightlife_score",
        "type": str,
        "default": None,
        "action": "append"
    },
    {
        "name": "shopping_score_label",
        "api_name": "shopping_score",
        "type": str,
        "default": None,
        "action": "append"
    },
    {
        "name": "culture_score_label",
        "api_name": "culture_score",
        "type": str,
        "default": None,
        "action": "append"
    },
    {
        "name": "dining_score_label",
        "api_name": "dining_score",
        "type": str,
        "default": None,
        "action": "append"
    },
    {
        "name": "avg_price",
        "api_name": "avg_price",
        "type": str,
        "default": None,
        "action": "append"
    },
    {
        "name": "tripadvisor_link",
        "api_name": "tripadvisor_link",
        "type": str,
        "default": None,
        "action": "append"
    }
]
