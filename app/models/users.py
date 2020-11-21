"""This module contains models related to users."""


from datetime import datetime
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from app.extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from app.models.events import EventStatus, saved_events
from app.models.roles import Permission
from app.models.sponsorships import SponsorshipStatus
from app.models.abstract_model import AbstractModel


class User(UserMixin, AbstractModel):
    """Class to represent a user of the application"""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    company = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    member_since = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    job_title = db.Column(db.String(64), nullable=True)
    website = db.Column(db.String(64), unique=True, nullable=True)
    about = db.Column(db.Text(), nullable=True)
    profile_photo_path = db.Column(db.Text(), unique=True, nullable=True)
    events = db.relationship(
        "Event", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    saved_events = db.relationship(
        "Event",
        secondary=saved_events,
        backref=db.backref("users", lazy="dynamic"),
        lazy="dynamic",
    )
    sponsorships = db.relationship(
        "Sponsorship", back_populates="sponsor", cascade="all, delete-orphan"
    )
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)

    # need to override these two methods bc setattr doesn't set properties
    @classmethod
    def create(cls, **data):
        """Create and return a new user."""
        user = cls()
        for attribute in data:
            if hasattr(user, attribute):
                setattr(user, attribute, data[attribute])
        user.password = data["password"]
        db.session.add(user)
        return user

    def update(self, **data):
        """Update the model from the given data."""
        for attribute in data:
            if hasattr(self, attribute):
                setattr(self, attribute, data[attribute])
        if "password" in data:
            self.password = data["password"]

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        """Set the password hash attribute."""
        self.password_hash = generate_password_hash(password)

    @property
    def full_name(self):
        """Return the user's full name."""
        return self.first_name + " " + self.last_name

    def verify_password(self, password):
        """Return True if the correct password is provided by the user."""
        return check_password_hash(self.password_hash, password)

    def generate_password_reset_token(self, expiration=3600):
        """Return a signed token for a user who wants to reset
        their password.
        """
        app = current_app._get_current_object()
        serializer = Serializer(app.config["SECRET_KEY"], expiration)
        return serializer.dumps({"reset": self.id}).decode("utf-8")

    @staticmethod
    def reset_password(token, new_password):
        """Decode token and change the user's password for password reset request.
        Returns True if the reset is successful, false otherwise
        """
        app = current_app._get_current_object()
        serializer = Serializer(app.config["SECRET_KEY"])
        try:
            data = serializer.loads(token.encode("utf-8"))
        except:
            return False
        user = User.query.get(data.get("reset"))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_change_email_token(self, new_email, expiration=3600):
        """Generate a signed token to allow a user to change their email
        address
        """
        app = current_app._get_current_object()
        serializer = Serializer(app.config["SECRET_KEY"], expiration)
        return serializer.dumps({"user_id": self.id, "new_email": new_email}).decode(
            "utf-8"
        )

    def change_email(self, token):
        """Decode token and change the user's email address. 
        Returns True if the update is successful, false otherwise.
        """
        app = current_app._get_current_object()
        serializer = Serializer(app.config["SECRET_KEY"])
        try:
            data = serializer.loads(token.encode("utf-8"))
        except:
            return False
        if data.get("user_id") != self.id:
            return False
        new_email = data.get("new_email")
        if new_email is None:
            return False
        # check to see if another user has this email
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = data.get("new_email")
        db.session.add(self)
        return True

    def is_organizer(self, event):
        """Return True if the user is the owner of the given event."""
        return event.user_id == self.id

    def can(self, perm):
        """Return True if the user has the given permissions
        """
        return self.role.has_permissions(perm)

    def is_administrator(self):
        """Return True if the user has administrator permissions"""
        return self.can(Permission.ADMIN)

    def save(self, event):
        """Add the given event to the user's saved events."""
        self.saved_events.append(event)

    def unsave(self, event):
        """Remove the given event from the user's saved events."""
        self.saved_events.remove(event)

    def has_saved(self, event):
        """Return True if the given event is in the list of the user's saved events. 
        Return False otherwise.
        """
        return event in self.saved_events

    def num_events_hosted(self, status=None):
        """Return the number of events hosted by the user that are 
        of the given status. This method is to only be called
        for a user with the permission to create events.
        """
        if status == EventStatus.LIVE:
            return len([event for event in self.events if event.is_ongoing()])
        elif status == EventStatus.PAST:
            return len([event for event in self.events if event.has_ended()])
        else:
            return len([event for event in self.events if not event.is_draft()])

    def num_events_sponsored(self, status=None):
        """Return the uniquenumber of events sponsored by the user that are 
        of the given status. This method is to only be called
        for a user with the permission to sponsor events.
        """
        num_events = 0
        if status == SponsorshipStatus.CURRENT:
            for sponsorship in self.sponsorships:
                if sponsorship.is_current():
                    num_events += 1
        elif status == SponsorshipStatus.PAST:
            for sponsorship in self.sponsorships:
                if sponsorship.is_past():
                    num_events += 1
        else:  # all
            for sponsorship in self.sponsorships:
                num_events += 1
        return num_events

    def has_purchased(self, package):
        """Return True if the user has already purchased the given package."""
        return any(
            [sponsorship.package == package for sponsorship in self.sponsorships]
        )

    @property
    def profile_photo(self):
        """Return the directory that the user's profile photo is in along with the image name.
        Example: images/my_photo.jpg
        """
        images_directory_index = 6
        filepath = None
        photo = self.profile_photo_path
        if photo is not None:
            photo_dir = photo.split("/")[images_directory_index:]
            filepath = "/".join(photo_dir)
        return filepath

    def get_events_by_status(self, status):
        """Return a list of hosted events based on the given status."""
        if status == EventStatus.LIVE:
            events = [event for event in self.events if event.is_ongoing()]
        elif status == EventStatus.DRAFT:
            events = [event for event in self.events if event.is_draft()]
        elif status == EventStatus.PAST:
            events = [event for event in self.events if event.has_ended()]
        else:
            events = self.events.all()
        return events

    def get_sponsorships_by_status(self, status):
        """Return a list of sponsorships based on the given status."""
        if status == SponsorshipStatus.CURRENT:
            sponsorships = [
                sponsorship
                for sponsorship in self.sponsorships
                if sponsorship.is_current()
            ]
        elif status == SponsorshipStatus.PAST:
            sponsorships = [
                sponsorship
                for sponsorship in self.sponsorships
                if sponsorship.is_past()
            ]
        else:
            sponsorships = self.sponsorships
        return sponsorships

    def __repr__(self):
        """Return a string representation of a user> Used for debugging
        purposes."""
        return "<User %r>" % (self.first_name + " " + self.last_name)


class AnonymousUser(AnonymousUserMixin):
    """Class that extends Flask Login's AnonymousUserMixin functionality."""

    # Anonymous users always have no permissions
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser
