import os
import math
from datetime import datetime, timedelta
from flask import current_app, abort
from sqlalchemy.ext.hybrid import hybrid_method
from app.search import add_to_index, remove_from_index, query_index, delete_index
from flask_login import UserMixin, AnonymousUserMixin
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


#association table between users and events tables
saved_events = db.Table("saved_events",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), nullable=False),
    db.Column("event_id", db.Integer, db.ForeignKey("events.id"), nullable=False),
    db.PrimaryKeyConstraint("user_id", "event_id")
)


class EventStatus:
    """Class to represent an event's status."""

    LIVE = "live"
    PAST = "past"
    DRAFT = "draft"


class SponsorshipStatus:
    """Class to represent the status of a sponsorship."""

    CURRENT = "current"
    PAST = "past"
    PENDING = "pending"


class Permission():
    """Class to represent user permissions."""

    CREATE_EVENT = 1
    SPONSOR_EVENT = 2
    ADMIN = 4


class SearchableMixin():
    """Mixin class that extends the functionality of a model to be able
    to perform searches and updates on Elasticsearch.
    """
    @classmethod
    def search(cls, query, page, results_per_page):
        """Perform a search on Elasticsearch and return the corresponding objects
        as well as the number of results.
        """
        ids, total = query_index(cls.__tablename__, query, page, results_per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        whens = []
        for index, id_ in enumerate(ids):
            whens.append((id_, index))
        #order by + case statement used to preserve the order of the results
        #essentially sorts the output using the index as the key
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(whens, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        """Method to be called before any commits to the database. Stores all new
        objects to be added to, modified, and deleted from the database to a dictionaty
        that will persist after the commit.
        """
        session._changes = {
            "add": list(session.new),
            "update": list(session.dirty),
            "delete": list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        """Method to be called after any commits to the database. Iterates over the 
        changes dictionary stored in the session and performs the necessary actions on 
        Elasticsearch to make sure that both have the same data.
        """
        for obj in session._changes["add"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj.__doctype__, obj)
        for obj in session._changes["update"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj.__doctype__, obj)
        for obj in session._changes["delete"]:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj.__doctype__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        """Refresh an index with all of the data from this model's table."""
        for obj in cls.query:
            add_to_index(cls.__tablename__, cls.__doctype__, obj)

    @classmethod
    def delete_index(cls, index=None):
        """Delete the related index in Elasticsearch."""
        if index is None:
            index = cls.__tablename__
        delete_index(index)
        

db.event.listen(db.session, "before_commit", SearchableMixin.before_commit)
db.event.listen(db.session, "after_commit", SearchableMixin.after_commit)


class User(UserMixin, db.Model):
    """Class to represent a user of the application"""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    company = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    has_paid = db.Column(db.Boolean, default=False, nullable=False)
    member_since = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    job_title = db.Column(db.String(64), nullable=True)
    website = db.Column(db.String(64), unique=True, nullable=True)
    about = db.Column(db.Text(), nullable=True)
    profile_photo_path = db.Column(db.Text(), unique=True, nullable=True)
    events = db.relationship(
        "Event", 
        backref="user", 
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    saved_events = db.relationship(
        "Event",
        secondary=saved_events,
        backref=db.backref("users", lazy="dynamic"),
        lazy="dynamic"
    )
    sponsorships = db.relationship(
        "Sponsorship",
        back_populates="sponsor",
        cascade="all, delete-orphan"
    )
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False) 
    
    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        """Set the password hash attribute."""
        self.password_hash = generate_password_hash(password)

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
        events = set()
        if status == SponsorshipStatus.CURRENT:
            for sponsorship in self.sponsorships:
                if not sponsorship.is_pending() and sponsorship.is_current():
                    events.add(sponsorship.event)
        elif status == SponsorshipStatus.PAST:
            for sponsorship in self.sponsorships:
                if not sponsorship.is_pending() and sponsorship.is_past():
                    events.add(sponsorship.event)
        else:
            for sponsorship in self.sponsorships:
                if not sponsorship.is_pending():
                    events.add(sponsorship.event)
        return len(events)

    def has_purchased(self, package):
        """Return True if the user has already purchased the given package."""
        return any([sponsorship.package == package for sponsorship in self.sponsorships if not sponsorship.is_pending()])

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

    def __repr__(self):
        """Return a string representation of a user> Used for debugging
        purposes."""
        return "<User %r>" % (self.first_name + " " + self.last_name)


class AnonymousUser(AnonymousUserMixin):
    """Class that extends Flask Login's AnonymousUserMixin functionality."""

    #Anonymous users always have no permissions
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser




class Role(db.Model):
    """Class to represent the different user roles"""

    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    permissions = db.Column(db.Integer, default=0, nullable=False)
    users = db.relationship("User", backref="role", lazy="dynamic")


    @staticmethod
    def insert_roles():
        """Insert role names into the roles table"""
        role_names = {
            "Event Organizer": [Permission.CREATE_EVENT],
            "Sponsor": [Permission.SPONSOR_EVENT],
            "Administrator": [
                Permission.CREATE_EVENT, 
                Permission.SPONSOR_EVENT, 
                Permission.ADMIN
            ]
        }
        for role_name in role_names:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
            role.reset_permissions()
            for perm in role_names[role_name]:
                role.add_permissions(perm)
            db.session.add(role)
        db.session.commit()

    def add_permissions(self, perm):
        """Grant a user the given permissions."""
        if not self.has_permissions(perm):
            self.permissions += perm

    def remove_permissions(self, perm):
        """Remove the given permissions."""
        if self.has_permissions(perm):
            self.permissions -= perm

    def reset_permissions(self):
        """Reset all user permissions"""
        self.permissions = 0

    #need to review this
    def has_permissions(self, perm):
        """Return True if the user has the given permissions."""
        return self.permissions & perm == perm
   
    def __repr__(self):
        """Return a string representation of the role class. Used
        for debugging purposes
        """
        return "<Role: %r>" % self.name
    

class Image(db.Model):
    """Class to represent an image"""

    __tablename__ = "images"
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.Text(), unique=True, index=True, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False) 
    image_type_id = db.Column(
        db.Integer, db.ForeignKey("image_types.id"), nullable=False
    )
    event_id = db.Column(
        db.Integer, db.ForeignKey("events.id"), nullable=False
    )

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
        return "<Type: %r>" %self.name



class Video(db.Model):
    """Class to represent the videos table."""

    __tablename__ = "videos"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, index=True, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    event_id = db.Column(
        db.Integer, db.ForeignKey("events.id"), nullable=False
    )

    def __repr__(self):
        """Return a string representation of a Video object.
        Used for debugging purposes.
        """
        return "<Video at: %r>" %self.url


class Event(SearchableMixin, db.Model):
    """Class to represent an event"""

    __tablename__ = "events"
    __searchable__ = ["title"]
    __doctype__ = "event"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    start_datetime = db.Column(db.DateTime, index=True, nullable=True)
    end_datetime = db.Column(db.DateTime, index=True, nullable=True)
    attendees = db.Column(db.String(64), nullable=True)
    male_to_female = db.Column(db.String(64), nullable=True)
    description = db.Column(db.Text, nullable=True)
    pitch = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
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
        "Image", 
        backref="event", 
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    packages = db.relationship(
        "Package",
        backref="event",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    video = db.relationship(
        "Video",
        backref="event",
        lazy=True,
        uselist=False,
        cascade="all, delete-orphan"
    )
    sponsorships = db.relationship(
        "Sponsorship",
        back_populates="event"
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
        return db.and_(db.or_(cls.published, cls.published == False), cls.end_datetime <= datetime.now())

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
        #initialize low and high variables
        #iterate through event's packages
            #check if the price of a package is greater than high,
            #if not, check if it is greater than low
        #return price range

        low = self.packages[0].price
        high = self.packages[0].price

        for package in self.packages:
            if package.price > high:
                high = package.price
            elif package.price < low:
                low = package.price
        return "$" + str(math.floor(low)) + " - " + "$" + str(math.ceil(high))

    @property
    def main_image(self):
        """Return the filepaths for the main event image.
        Filepath will be used to render the image in Jinja templates.
        """
        filepath = None
        image_type = ImageType.query.filter_by(name="Main Event Image").first()
        image = self.images.filter_by(image_type=image_type).first()
        if image is not None:
            image_dir = image.path.split("/")[6:]
            filepath = "/".join(image_dir)
        return filepath

    @property
    def misc_images(self):
        """Return the filepaths for other miscaelaneous images associated with this event.
        Filepath will be used to render the image in Jinja templates.
        """
        filepaths = []
        image_type = ImageType.query.filter_by(name="Misc").first()
        images = self.images.filter_by(image_type=image_type).all()
        for image in images:
            image_dir = image.path.split("/")[6:]
            filepath = "/".join(image_dir)
            filepaths.append(filepath)
        return filepaths

    def num_sponsors(self):
        """Return the number of sponsors for this event."""
        sponsors = set()
        for sponsorship in self.sponsorships:
            if not sponsorship.is_pending():
                sponsors.add(sponsorship.sponsor)
        return len(sponsors)

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
            "Appearance or Signing",
            "Attraction",
            "Camp, Trip, or Retreat",
            "Class, Training or Workshop",
            "Concert or Performance",
            "Conference",
            "Convention",
            "Dinner or Gala",
            "Festival or Fair",
            "Game or Competition",
            "Meeting or Networking Event",
            "Other",
            "Party or Social Gathering",
            "Race or Endurance Event",
            "Rally",
            "Screening",
            "Seminar or Talk",
            "Tour",
            "Tournament",
            "Tradeshow, Consumer Show or Expo",
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
            "Auto, Boat & Air",
            "Business & Professional",
            "Charity & Causes",
            "Community & Culture",
            "Family & Education",
            "Fashion & Beauty",
            "Film, Media & Entertainment",
            "Food & Drink",
            "Government & Politics",
            "Health & Wellness",
            "Hobbies & Special Interest",
            "Home & Lifestyle",
            "Music",
            "Other",
            "Performing & Visual Arts",
            "Religion & Spirituality",
            "School Activities",
            "Science & Technology",
            "Seasonal & Holiday",
            "Sports & Fitness",
            "Travel & Outdoor",
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


class Venue(db.Model):
    """Class to represent a venue"""

    __tablename__ = "venues"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(64), unique=True, index=True, nullable=False)
    city = db.Column(db.String(64), nullable=False)
    state = db.Column(db.String(64), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    events = db.relationship(
        "Event", 
        backref="venue", 
        lazy="dynamic"
    )

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


class Package(db.Model):
    """Class to represent a sponsorship package."""

    __tablename__ = "packages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Numeric(4, 2), nullable=False)
    audience = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text, nullable=True)
    num_purchased = db.Column(db.Integer, default=0, nullable=False)
    available_packages = db.Column(db.Integer, nullable=False)
    package_type = db.Column(db.String(64), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    sponsorships = db.relationship(
        "Sponsorship",
        back_populates="package"
    )
   
    @staticmethod
    def insert_packages():
        """Method to insert default packages into the database."""
        deadline = datetime.now() + timedelta(days=30)
        packages = [
            ("Gold", 4000, "1-50", deadline, 10, "Cash"),
            ("Silver", 2000, "1-50", deadline, 10, "Cash"),
            ("Bronze", 1000, "1-50", deadline, 10, "Cash"),
            ("Social Media Shoutout", 500, "1-50", deadline, 10, "Cash"),
            ("Logo On Flyer", 500, "1-50", deadline, 10, "Cash")
        ]
        for name, price, attendees, time, available, type_ in packages:
            package = Package.query.filter_by(
                name=name,
                price=price,
                attendees=attendees,
                deadline=time,
                avaiable_packages=available,
                package_type=type_
            ).first()
            if package is None:
                package = Package(
                    name=name,
                    price=price,
                    attendees=attendees,
                    deadline=time,
                    avaiable_packages=available,
                    package_type=type_
                )
                db.session.add(package)
        db.session.commit()

    def is_sold_out(self):
        """Return True if the package is sold out."""
        return self.num_purchased == self.available_packages

    def num_for_sale(self):
        """Return the number of available packages."""
        return self.available_packages - self.num_purchased
    

    def __repr__(self):
        """Return the string representation of a Package.
        Used for debugging purposes.
        """
        return "<Package Name: %r>" %self.name


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
        return "<[Event: %r, Sponsor: %r, Package: %r]>" %(self.event_id, self.sponsor_id, self.package_id)



