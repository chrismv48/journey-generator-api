"""Database models for IQ Analytics"""
from sqlalchemy import func
from sqlalchemy.dialects import postgresql
from base import SerializedModel
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

db = SQLAlchemy()


class Destinations(db.Model, SerializedModel):
    __tablename__ = "destinations"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    city_name = db.Column(db.String)
    ascii_name = db.Column(db.String)
    latitude = db.Column(db.String)
    longitude = db.Column(db.String)
    country_code = db.Column(db.String)
    population = db.Column(db.Integer)
    timezone = db.Column(db.String)
    modification_date = db.Column(db.Date)
    country_name = db.Column(db.String)
    continent_name = db.Column(db.String)
    backpacker_price = db.Column(db.Float)
    normal_price = db.Column(db.Float)
    safety_index = db.Column(db.Float)
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
    life_score = db.Column(db.Float)
    nightlife_score= db.Column(db.Float)
    leisure_score = db.Column(db.Float)
    safety_score = db.Column(db.Float)
    friendly_to_foreigners_score = db.Column(db.Float)
    racism_score = db.Column(db.Float)
    lgbt_friendly_score = db.Column(db.Float)
    female_friendly_score = db.Column(db.Float)
    tags = db.Column(postgresql.ARRAY(db.String))



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

    destination = db.relationship('Destinations', backref=db.backref('climate'))


class Countries(db.Model, SerializedModel):
    __tablename__ = "countries"

    country_code = db.Column(db.String, primary_key=True)
    country_name = db.Column(db.String)
    continent_name = db.Column(db.String)
    continent = db.Column(db.String)
