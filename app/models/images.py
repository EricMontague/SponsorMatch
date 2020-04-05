"""This module contains models related to images."""


from datetime import datetime
from app.extensions import db


class Image(db.Model):
    """Class to represent an image"""

    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.Text(), unique=True, index=True, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    image_type_id = db.Column(
        db.Integer, db.ForeignKey("image_types.id"), nullable=False
    )
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)

    def __repr__(self):
        """Return a string representation of the Image class.
        Used for debugging purposes
        """
        return "<Image at: %r>" % self.path


class ImageType(db.Model):
    """Class to represent the type of an image"""

    __tablename__ = "image_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    images = db.relationship("Image", backref="image_type", lazy="dynamic")

    @staticmethod
    def insert_image_types():
        """Method to insert image types into the database.
        Profile is for a user's profile photo, logo is for a company's
        logo when posting an event, and Event is for miscellaneous images
        associated with the event.
        """
        image_types = ["Main Event Image", "Misc"]
        for image_type in image_types:
            type_ = ImageType.query.filter_by(name=image_type).first()
            if type_ is None:
                type_ = ImageType(name=image_type)
                db.session.add(type_)
        db.session.commit()

    def __repr__(self):
        """Retur na string representation of an ImageType object.
        Used for debugging purposes.
        """
        return "<Type: %r>" % self.name
        