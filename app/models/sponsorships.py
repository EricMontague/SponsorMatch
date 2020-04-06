"""This module contains models related to sponsorships."""


from app.extensions import db
from sqlalchemy.ext.hybrid import hybrid_method


class SponsorshipStatus:
    """Class to represent the status of a sponsorship."""

    CURRENT = "current"
    PAST = "past"
    PENDING = "pending"


class Sponsorship(db.Model):
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
        """Return True if the sponsorship is for a event that has a status of live, 
        return False otherwise.
        """
        return not self.is_pending() and self.event.is_ongoing()

    def is_past(self):
        """Return True if the sponsorship is for an event that has a status of past,
        return False otherwise.
        """
        return not self.is_pending() and self.event.has_ended()

    @hybrid_method
    def is_pending(self):
        """Return True if the sponsorship is pending. Used for when a sponsor is in the middle
        of purchasing sponsorships packages in the checkout window.
        """
        return self.timestamp is None and self.confirmation_code is None

    @is_pending.expression
    def is_pending(cls):
        """Return True if the sponsorship is pending. Used for when a sponsor is in the middle
        of purchasing sponsorships packages in the checkout window.
        """
        return db.and_(cls.timestamp == None, cls.confirmation_code == None)

    def __repr__(self):
        """Returns a string representation of a sponsorship deal. Used for debugging
        purposes.
        """
        return "<[Event: %r, Sponsor: %r, Package: %r]>" % (
            self.event_id,
            self.sponsor_id,
            self.package_id,
        )
