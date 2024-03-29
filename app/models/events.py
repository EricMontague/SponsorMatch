"""This module contains models related to events."""


import math
from sqlalchemy.ext.hybrid import hybrid_method
from datetime import datetime
from app.extensions import db
from app.models.images import ImageType, Image
from app.models.abstract_model import AbstractModel


class EventStatus:
    """Class to represent an event's status."""

    LIVE = "live"
    PAST = "past"
    DRAFT = "draft"


# association table between users and events tables
saved_events = db.Table(
    "saved_events",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), nullable=False),
    db.Column("event_id", db.Integer, db.ForeignKey("events.id"), nullable=False),
    db.PrimaryKeyConstraint("user_id", "event_id"),
)


class Event(AbstractModel):
    """Class to represent an event"""

    __tablename__ = "events"
    __searchable__ = [
        "title",
        "description",
        "venue.state",
        "venue.city",
        "start_datetime",
        "end_datetime",
        "event_category_id",
        "event_type_id",
        "published",
    ]
    __doctype__ = "event"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    start_datetime = db.Column(db.DateTime, index=True, nullable=True)
    end_datetime = db.Column(db.DateTime, index=True, nullable=True)
    attendees = db.Column(db.String(64), nullable=True)
    male_to_female = db.Column(db.String(64), nullable=True)
    description = db.Column(db.Text, nullable=True)
    pitch = db.Column(db.Text, nullable=True)
    published = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venues.id"), nullable=False)
    event_type_id = db.Column(
        db.Integer, db.ForeignKey("event_types.id"), nullable=False
    )
    event_category_id = db.Column(
        db.Integer, db.ForeignKey("event_categories.id"), nullable=False
    )
    images = db.relationship(
        "Image", backref="event", lazy="dynamic", cascade="all, delete-orphan"
    )
    packages = db.relationship(
        "Package", backref="event", lazy="dynamic", cascade="all, delete-orphan"
    )
    video = db.relationship(
        "Video", backref="event", lazy=True, uselist=False, cascade="all, delete-orphan"
    )
    sponsorships = db.relationship(
        "Sponsorship", back_populates="event", cascade="all, delete-orphan"
    )

    @hybrid_method
    def is_ongoing(self):
        """Return True if the event is ongoing."""
        return self.published and self.end_datetime > datetime.now()

    @is_ongoing.expression
    def is_ongoing(cls):
        """Return True if the event is ongoing."""
        return db.and_(cls.published, cls.end_datetime > datetime.now())

    @hybrid_method
    def has_ended(self):
        """Return True if the event has ended."""
        return self.published and self.end_datetime <= datetime.now()

    @has_ended.expression
    def has_ended(cls):
        """Return True if the event has ended."""
        return db.and_(
            db.or_(cls.published, cls.published == False),
            cls.end_datetime <= datetime.now(),
        )

    def is_draft(self):
        """Return True if the event is in draft status."""
        return not self.published

    def start_date(self, string_format=None):
        """Return the event's start date as a date object. If a format is passed in,
        then the date will be returned in the given string format.
        """
        if string_format:
            return self.start_datetime.strftime(string_format)
        else:
            return self.start_datetime.date()

    def end_date(self, string_format=None):
        """Return the event's end date as a date object. If a format is passed in,
        then the date will be returned in the given string format.
        ."""
        if string_format:
            return self.end_datetime.strftime(string_format)
        else:
            return self.end_datetime.date()

    def start_time(self, string_format=None):
        """Return the event's start time as a time object. If a format is passed in,
        then the time will be returned in the given string format."""
        if string_format:
            return self.start_datetime.strftime(string_format)
        else:
            return self.start_datetime.time()

    def end_time(self, string_format=None):
        """Return the event's end time. If a format is passed in,
        then the time will be returned in the given string format."""
        if string_format:
            return self.end_datetime.strftime(string_format)
        else:
            return self.end_datetime.time()

    def total_sales(self):
        """Return the total package sales for the event."""
        return sum([package.num_purchased * package.price for package in self.packages])

    def num_packages_sold(self):
        """Return the number of packages sold for this event."""
        return sum([package.num_purchased for package in self.packages])

    def num_packages_available(self):
        """Return the number of packages available for this event."""
        return sum([package.available_packages for package in self.packages])

    def price_range(self):
        """Return the price range for the event's packages."""
        low = self.packages[0].price
        high = self.packages[0].price

        for package in self.packages:
            if package.price > high:
                high = package.price
            elif package.price < low:
                low = package.price
        return "$" + str(math.floor(low)) + " - " + "$" + str(math.ceil(high))

    def main_image(self):
        """Return the filepath for the main event image."""
        for image in self.images:
            if image.image_type.name == "Main Event Image":
                return "/".join(image.path.split("/")[-3:]).replace("static/", "")
        return ""

    def misc_images(self):
        """Return the filepaths for other miscaelaneous images associated with this event."""
        images = [
            "/".join(image.path.split("/")[-3:]).replace("static/", "")
            for image in self.images if image.image_type.name == "Misc"
        ]
        return images

    def num_sponsors(self):
        """Return the number of sponsors for this event."""
        return len(self.sponsorships)

    def __repr__(self):
        """Return a string representation of an Event object.
        Useful for debugging.
        """
        return "<Event: %r>" % self.title


class EventType(db.Model):
    """Class to represent an event type"""

    __tablename__ = "event_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    events = db.relationship("Event", backref="event_type", lazy="dynamic")

    def __repr__(self):
        """Return a string representation of an EventType object.
        Used for debugging purposes.
        """
        return "<Event Type: %r>" % self.name

    @staticmethod
    def insert_event_types():
        """Method to insert event types into the database"""
        event_types = [
            "Attraction",
            "Concert or Performance",
            "Convention",
            "Dinner or Gala",
            "Festival or Fair",
            "Meeting or Networking Event"
        ]

        for event_type in event_types:
            type_ = EventType.query.filter_by(name=event_type).first()
            if type_ is None:
                type_ = EventType(name=event_type)
                db.session.add(type_)
        db.session.commit()


class EventCategory(db.Model):
    """Class to represent an event category"""

    __tablename__ = "event_categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True, nullable=False)
    events = db.relationship("Event", backref="event_category", lazy="dynamic")

    @staticmethod
    def insert_event_categories():
        """Method to insert event categories into the database"""
        categories = [
            "Business & Professional",
            "Charity & Causes",
            "Film, Media & Entertainment",
            "Food & Drink",
            "Home & Lifestyle",
            "Performing & Visual Arts"
        ]

        for category in categories:
            event_category = EventCategory.query.filter_by(name=category).first()
            if event_category is None:
                event_category = EventCategory(name=category)
                db.session.add(event_category)
        db.session.commit()

    def __repr__(self):
        """Return a string representation of an EventCategory object.
        Useful for debugging purposes.
        """
        return "<Event Category: %r>" % self.name
