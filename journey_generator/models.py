"""Database models for IQ Analytics"""
from sqlalchemy import func
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import deferred
from sqlalchemy.ext.hybrid import hybrid_property

from base import SerializedModel
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()


class Destinations(db.Model, SerializedModel):
    __tablename__ = "destinations"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    city_name = deferred(db.Column(db.String))
    ascii_name = db.Column(db.String)
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    country_code = db.Column(db.String)
    state = db.Column(db.String)
    population = db.Column(db.Integer)
    timezone = db.Column(db.String)
    modification_date = db.Column(db.Date)
    country_name = db.Column(db.String)
    continent_name = db.Column(db.String)
    backpacker_price = db.Column(db.Float)
    normal_price = db.Column(db.Float)
    overall_crime = db.Column(db.Float)
    crime_increasing_3yrs = db.Column(db.Float)
    home_theft = db.Column(db.Float)
    robbery = db.Column(db.Float)
    car_stolen = db.Column(db.Float)
    car_theft = db.Column(db.Float)
    assault = db.Column(db.Float)
    insulted = db.Column(db.Float)
    hate_crime = db.Column(db.Float)
    drugs = db.Column(db.Float)
    property_crimes = db.Column(db.Float)
    violent_crimes = db.Column(db.Float)
    corruption_bribery = db.Column(db.Float)
    walking_day = db.Column(db.Float)
    walking_night = db.Column(db.Float)
    air_quality = db.Column(db.Float)
    drinking_water_quality = db.Column(db.Float)
    garbage_disposal = db.Column(db.Float)
    cleanliness = db.Column(db.Float)
    quiet = db.Column(db.Float)
    water_quality = db.Column(db.Float)
    comfortable_in_city = db.Column(db.Float)
    quality_of_greenery = db.Column(db.Float)
    safety_score = db.Column(db.Float)
    tags = db.Column(postgresql.ARRAY(db.String))
    amusement_park = db.Column(db.Float)
    aquarium = db.Column(db.Float)
    art_gallery = db.Column(db.Float)
    bar = db.Column(db.Float)
    cafe = db.Column(db.Float)
    clothing_store = db.Column(db.Float)
    department_store = db.Column(db.Float)
    jewelry_store = db.Column(db.Float)
    lodging = db.Column(db.Float)
    museum = db.Column(db.Float)
    night_club = db.Column(db.Float)
    park = db.Column(db.Float)
    restaurant = db.Column(db.Float)
    shopping_mall = db.Column(db.Float)
    spa = db.Column(db.Float)
    stadium = db.Column(db.Float)
    zoo = db.Column(db.Float)
    amusement_park_index = db.Column(db.Float)
    aquarium_index = db.Column(db.Float)
    art_gallery_index = db.Column(db.Float)
    bar_index = db.Column(db.Float)
    cafe_index = db.Column(db.Float)
    clothing_store_index = db.Column(db.Float)
    department_store_index = db.Column(db.Float)
    jewelry_store_index = db.Column(db.Float)
    lodging_index = db.Column(db.Float)
    museum_index = db.Column(db.Float)
    night_club_index = db.Column(db.Float)
    park_index = db.Column(db.Float)
    restaurant_index = db.Column(db.Float)
    shopping_mall_index = db.Column(db.Float)
    spa_index = db.Column(db.Float)
    stadium_index = db.Column(db.Float)
    zoo_index = db.Column(db.Float)
    amusement_park_label = db.Column(db.Float)
    aquarium_label = db.Column(db.Float)
    art_gallery_label = db.Column(db.Float)
    bar_label = db.Column(db.Float)
    cafe_label = db.Column(db.Float)
    clothing_store_label = db.Column(db.Float)
    department_store_label = db.Column(db.Float)
    jewelry_store_label = db.Column(db.Float)
    lodging_label = db.Column(db.Float)
    museum_label = db.Column(db.Float)
    night_club_label = db.Column(db.Float)
    park_label = db.Column(db.Float)
    restaurant_label = db.Column(db.Float)
    shopping_mall_label = db.Column(db.Float)
    spa_label = db.Column(db.Float)
    stadium_label = db.Column(db.Float)
    zoo_label = db.Column(db.Float)
    attractions_score = db.Column(db.Float)
    nightlife_score = db.Column(db.Float)
    shopping_score = db.Column(db.Float)
    culture_score = db.Column(db.Float)
    dining_score = db.Column(db.Float)
    lodging_score = db.Column(db.Float)
    spas_score = db.Column(db.Float)
    attractions_score_label = db.Column(db.Integer)
    nightlife_score_label = db.Column(db.Integer)
    shopping_score_label = db.Column(db.Integer)
    culture_score_label = db.Column(db.Integer)
    dining_score_label = db.Column(db.Integer)
    lodging_score_label = db.Column(db.Integer)
    spas_score_label = db.Column(db.Integer)
    places_index = db.Column(db.Float)
    places_index_label = db.Column(db.Integer)
    population_label = db.Column(db.Integer)
    safety_score_label = db.Column(db.Integer)
    environment_score = db.Column(db.Float)
    environment_score_label = db.Column(db.Integer)

    @hybrid_property
    def avg_price(self):
        if self.backpacker_price and self.normal_price:
            return (self.backpacker_price + self.normal_price) / 2
        else:
            return None


class Climate(db.Model, SerializedModel):
    __tablename__ = "climate"
    __table_args__ = (db.UniqueConstraint('city_id', 'month', name='city_id_month_uc'),)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city_id = db.Column(db.Integer, db.ForeignKey('destinations.id'))
    month = db.Column(db.String)
    low_temp = db.Column(db.Integer, index=True)
    high_temp = db.Column(db.Integer, index=True)
    temp_index = db.Column(db.Float, index=True)
    apparent_low_temp = db.Column(db.Integer, index=True)
    apparent_high_temp = db.Column(db.Integer, index=True)
    humidity = db.Column(db.Float, index=True)
    humidity_index = db.Column(db.Float, index=True)
    dew_point = db.Column(db.Float, index=True)
    wind_speed = db.Column(db.Float, index=True)
    wind_speed_index = db.Column(db.Float, index=True)
    rain_probability = db.Column(db.Float, index=True)
    rain_probability_index = db.Column(db.Float, index=True)
    cloud_cover = db.Column(db.Float, index=True)
    cloud_cover_index = db.Column(db.Float, index=True)
    weather_index = db.Column(db.Float, index=True)
    weather_index_label = db.Column(db.Integer, index=True)

    destination = db.relationship('Destinations', backref=db.backref('climate', lazy='joined'), lazy='joined')


class Countries(db.Model, SerializedModel):
    __tablename__ = "countries"

    country_code = db.Column(db.String, primary_key=True)
    country_name = db.Column(db.String)
    continent_name = db.Column(db.String)
    continent = db.Column(db.String)


class GeoMindCities(db.Model, SerializedModel):
    __tablename__ = "geomind_cities"

    geoname_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    city_name = db.Column(db.String)
    ascii_name = db.Column(db.String)
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    country_code = db.Column(db.String)
    state = db.Column(db.String)
    population = db.Column(db.Integer)
    timezone = db.Column(db.String)
    geomind_modification_date = db.Column(db.Date)
