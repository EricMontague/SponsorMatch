"""This module contains models related to venues."""


from app.extensions import db
from app.models.abstract_model import AbstractModel


class Venue(AbstractModel):
    """Class to represent a venue"""

    __tablename__ = "venues"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(64), unique=True, index=True, nullable=False)
    city = db.Column(db.String(64), nullable=False)
    state = db.Column(db.String(64), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    events = db.relationship("Event", backref="venue", lazy="dynamic")

    def to_dict(self):
        """Return the attributes of the model as a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "events": self.events,
        }

    def __repr__(self):
        """Return a string representation of an Address object.
        Used for debugging purposes.
        """
        return "<Venue: %r>" % (
            self.name
            + " at "
            + self.address
            + ", "
            + self.city
            + ", "
            + self.state
            + " "
            + self.zip_code
        )

