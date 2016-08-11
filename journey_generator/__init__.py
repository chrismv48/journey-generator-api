from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from journey_generator.models import db

app = Flask(__name__)
app.config.from_pyfile('settings.py')
db.init_app(app)

with app.app_context():
    db.create_all()
