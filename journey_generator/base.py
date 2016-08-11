"""Docstring goes here"""
from datetime import datetime, date
import json

from flask_restful import Resource, abort
from sqlalchemy.exc import IntegrityError
from flask import request

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseResource(Resource):
    # def __init__(self, model_name, model_class, alternate_pk, associated_objects, resource_fields):

    model_name = None
    model_class = None
    alternate_pk = None
    associated_objects = []

    def get(self, id=None):
        if id:
            result = self.model_class.query.get(id)
            if not result:
                abort(404, message="{} {} not found".format(self.model_name, id))
            return result.as_dict(self.associated_objects)
        else:
            return {self.model_name: [result.as_dict(self.associated_objects) for result in
                                      self.model_class.query.all()]}

    def put(self, id):
        current_model = self.model_class.query.get(id)
        if not current_model:
            abort(404, message="Object {} not found".format(id))
        updated_model = current_model.from_dict(request.json)
        db.session.add(updated_model)
        db.session.commit()
        return updated_model.as_dict()

    def post(self):
        current_model = self.model_class(**request.json)
        db.session.add(current_model)
        try:
            db.session.commit()
            return current_model.as_dict()
        except IntegrityError as e:
            return abort(404, message="{} already exists: {}".format(self.model_name, e.message))
        finally:
            db.session.rollback()

    def delete(self, id):
        current_model = self.model_class.query.get(id)
        if not current_model:
            abort(404, message="Object {} not found".format(id))
        db.session.delete(current_model)
        db.session.commit()
        return current_model.as_dict()


class SerializedModel(object):
    """A SQLAlchemy model mixin class that can serialize itself as JSON."""

    @property
    def table_fields(self):
        return [key for key in self.__table__.columns.keys() if not key.startswith('_')]

    def as_dict(self, associated_columns=None):
        """Return dict representation of class by iterating over database
        columns."""
        value = {}
        for column in self.__table__.columns:
            attribute = getattr(self, column.name)
            if isinstance(attribute, datetime):
                attribute = attribute.strftime("%m/%d/%Y %H:%M:%S")
            if isinstance(attribute, date):
                attribute = attribute.strftime("%m/%d/%Y")
            value[column.name] = attribute
        if associated_columns:
            for column in associated_columns:
                attributes = getattr(self, column)
                try:
                    value[column] = [attribute.as_dict() for attribute in attributes]
                except TypeError:
                    value[column] = attributes.as_dict()
        return value

    def from_dict(self, attributes):
        """Update the current instance based on attribute->value items in
        *attributes*."""
        for attribute in attributes:
            if attribute in self.table_fields:
                setattr(self, attribute, attributes[attribute])
        return self

    def as_json(self):
        """Return JSON representation taken from dict representation."""
        return json.dumps(self.as_dict())
