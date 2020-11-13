"""This module contains a class which subclasses
SQLAlchemy's Model class to provide some 
extra functionality.
"""
from abc import ABC
from app.extensions import db


class AbstractModel(ABC, db.Model):
    """Abstract base class that provides extra functionality
    to SQLAlchemy's Model class.
    """

    @classmethod
    def create(cls, **data):
        """Return a new model."""
        model = cls()
        for attribute in data:
            if hasattr(model, attribute):
                setattr(model, attribute, data[attribute])
        db.session.add(model)
        return model

    def update(self, **data):
        """Update the model from the given data."""
        for attribute in data:
            if hasattr(self, attribute):
                setattr(self, attribute, data[attribute])
