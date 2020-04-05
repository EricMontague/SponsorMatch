"""This module contains models related to videos."""


from datetime import datetime
from app.extensions import db


class Video(db.Model):
    """Class to represent the videos table."""

    __tablename__ = "videos"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, index=True, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)

    def __repr__(self):
        """Return a string representation of a Video object.
        Used for debugging purposes.
        """
        return "<Video at: %r>" % self.url
