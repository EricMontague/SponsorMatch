"""This module contains models related to sponsorships."""


from app.extensions import db
from sqlalchemy.ext.hybrid import hybrid_method
from app.models.abstract_model import AbstractModel


class SponsorshipStatus:
    """Class to represent the status of a sponsorship."""

    CURRENT = "current"
    PAST = "past"


class Sponsorship(AbstractModel):
    """Class to represent a sponsorship deal."""

    __tablename__ = "sponsorships"
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey("packages.id"), primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=True)
    confirmation_code = db.Column(db.String(64), nullable=True)
    event = db.relationship("Event", back_populates="sponsorships")
    sponsor = db.relationship("User", back_populates="sponsorships")
    package = db.relationship("Package", back_populates="sponsorships")

    def is_current(self):
        """Return True if the sponsorship is for an event that has a status of live, 
        return False otherwise.
        """
        return self.event.is_ongoing()

    def is_past(self):
        """Return True if the sponsorship is for an event that has a status of past,
        return False otherwise.
        """
        return self.event.has_ended()

    def __repr__(self):
        """Returns a string representation of a sponsorship deal. Used for debugging
        purposes.
        """
        return "<[Event: %r, Sponsor: %r, Package: %r]>" % (
            self.event_id,
            self.sponsor_id,
            self.package_id,
        )

