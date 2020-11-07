"""This module contains test data to be used throughout the tests
as well as classes for creating fake models for testing.
"""


import uuid
from datetime import date, timedelta, datetime
from app.models import (
    User,
    Role,
    Event,
    EventType,
    EventCategory,
    Venue,
    Package,
    Image,
    ImageType,
    Sponsorship,
    Permission,
    SponsorshipStatus,
    EventStatus,
)


class ViewFunctionTestData:
    """Class to hold test parameters for testing view functions"""

    INVALID_LOGINS = [
        {
            "email": "dave@gmail.com",
            "password": "books",
            "error_message": "Invalid email or password.",
        },
        {
            "email": "dave",
            "password": "password",
            "error_message": "Invalid email address.",
        },
        {
            "email": "dave" * 25,
            "password": "password",
            "error_message": "Field must be between 1 and 64 characters long.",
        },
    ]
    VALID_LOGINS = [
        {
            "role_name": "Event Organizer",
            "email": "greg@gmail.com",
            "password": "password",
            "message": "Please complete your signup process by purchasing your subscription below.",
        },
        {
            "role_name": "Sponsor",
            "email": "greg@gmail.com",
            "password": "password",
            "message": "Greg",
        },
    ]
    INVALID_REGISTRATIONS = [
        {
            "first_name": "Dave",
            "last_name": "McBride",
            "company": "Facebook",
            "email": "dave@gmail.com",
            "password": "password",
            "confirm_password": "password",
            "role": 0,  # didn't select a role
            "error_message": "Please select an account type.",
        },
        {
            "first_name": "Dave" * 25,
            "last_name": "McBride",
            "company": "Facebook",
            "email": "dave@gmail.com",
            "password": "password",
            "confirm_password": "password",
            "role": 1,  # event organizer
            "error_message": "Field must be between 1 and 64 characters long.",
        },
        {
            "first_name": "Dave",
            "last_name": "McBride" * 25,
            "company": "Facebook",
            "email": "dave@gmail.com",
            "password": "password",
            "confirm_password": "password",
            "role": 1,  # event organizer
            "error_message": "Field must be between 1 and 64 characters long.",
        },
        {
            "first_name": "Dave",
            "last_name": "McBride",
            "company": "Facebook" * 25,
            "email": "dave@gmail.com",
            "password": "password",
            "confirm_password": "password",
            "role": 1,  # event organizer
            "error_message": "Field must be between 1 and 64 characters long.",
        },
        {
            "first_name": "Dave",
            "last_name": "McBride",
            "company": "Facebook",
            "email": "dave@gmail.com" * 25,
            "password": "password",
            "confirm_password": "password",
            "role": 1,  # event organizer
            "error_message": "Field must be between 1 and 64 characters long.",
        },
        {
            "first_name": "Dave",
            "last_name": "McBride",
            "company": "Facebook",
            "email": "dave",
            "password": "password",
            "confirm_password": "password",
            "role": 1,  # event organizer
            "error_message": "Invalid email address.",
        },
        {
            "first_name": "Dave",
            "last_name": "McBride",
            "company": "Facebook",
            "email": "dave@gmail.com",
            "password": "cat",
            "confirm_password": "password",
            "role": 1,  # event organizer
            "error_message": "Passwords must match.",
        },
        {
            "first_name": "Dave",
            "last_name": "McBride",
            "company": "Amazon",
            "email": "dave@gmail.com",
            "password": "password",
            "confirm_password": "password",
            "role": 1,  # event organizer
            "error_message": "Company already registered.",
        },
        {
            "first_name": "Dave",
            "last_name": "McBride",
            "company": "Facebook",
            "email": "dave@amazon.com",
            "password": "password",
            "confirm_password": "password",
            "role": 1,  # event organizer
            "error_message": "Email already registered.",
        },
    ]
    VALID_REGISTRATIONS = [
        {
            "first_name": "Dave",
            "last_name": "McBride",
            "company": "Facebook",
            "email": "dave@gmail.com",
            "password": "password",
            "confirm_password": "password",
            "role": 1,  # event organizer
            "message": "Registration successful!. You will be asked for your payment information upon login.",
        },
        {
            "first_name": "Bob",
            "last_name": "Smith",
            "company": "Google",
            "email": "bob@gmail.com",
            "password": "password",
            "confirm_password": "password",
            "role": 2,  # sponsor
            "message": "Registration successful!. Please login.",
        },
    ]
    INVALID_CLOSE_ACCOUNT_DATA = [{"confirm": "close"}, {"confirm": "Foo"}]
    VALID_CHANGE_PASSWORD_DATA = {
        "old_password": "password",
        "new_password": "bars",
        "confirm_password": "bars",
        "message": "Your password has been successfully changed.",
    }
    INVALID_CHANGE_PASSWORD_DATA = [
        {
            "old_password": "password",
            "new_password": "bars",
            "confirm_password": "fooooooo",
            "error_message": "Passwords must match.",
        },
        {
            "old_password": "BOB",
            "new_password": "pass",
            "confirm_password": "pass",
            "error_message": "You entered an invalid password.",
        },
    ]
    VALID_EVENT_DATA = {
        "title": "Test Event",
        "event_type": 1,  # Appearance or Signing
        "category": 1,  # Auto, Boat & Air
        "venue_name": "The Kimmel Center",
        "address": "300 S. Broad St",
        "city": "Philadelphia",
        "state": 39,  # pennsylvania
        "zip_code": "19102",
        "start_date": date.today() + timedelta(days=1),
        "end_date": date.today() + timedelta(days=2),
        "start_time": 1,  # 12:00 AM
        "end_time": 2,  # 12:30 AM
    }
    INVALID_EVENT_DATA = [
        {
            "title": "Test Event",
            "event_type": 0,  # didn't select anything
            "category": 1,  # Auto, Boat & Air
            "venue_name": "The Kimmel Center",
            "address": "300 S. Broad St",
            "city": "Philadelphia",
            "state": 39,  # pennsylvania
            "zip_code": "19102",
            "start_date": date.today() + timedelta(days=1),
            "end_date": date.today() + timedelta(days=2),
            "start_time": 1,  # 12:00 AM
            "end_time": 2,  # 12:30 AM
            "error_message": "Please select an event type.",
        },
        {
            "title": "Test Event",
            "event_type": 1,  # Appearance or Signing
            "category": 0,  # didn't select anything
            "venue_name": "The Kimmel Center",
            "address": "300 S. Broad St",
            "city": "Philadelphia",
            "state": 39,  # pennsylvania
            "zip_code": "19102",
            "start_date": date.today() + timedelta(days=1),
            "end_date": date.today() + timedelta(days=2),
            "start_time": 1,  # 12:00 AM
            "end_time": 2,  # 12:30 AM
            "error_message": "Please select an event category.",
        },
        {
            "title": "Test Event",
            "event_type": 1,  # Appearance or Signing
            "category": 1,  # Auto, Boat & Air
            "venue_name": "The Kimmel Center",
            "address": "300 S. Broad St",
            "city": "Philadelphia",
            "state": 0,  # didn't select a state
            "zip_code": "19102",
            "start_date": date.today() + timedelta(days=1),
            "end_date": date.today() + timedelta(days=2),
            "start_time": 1,  # 12:00 AM
            "end_time": 2,  # 12:30 AM
            "error_message": "Please select a state.",
        },
        {
            "title": "Test Event",
            "event_type": 1,  # Appearance or Signing
            "category": 1,  # Auto, Boat & Air
            "venue_name": "The Kimmel Center",
            "address": "300 S. Broad St",
            "city": "Philadelphia",
            "state": 39,  # pennsylvania
            "zip_code": "19102",
            "start_date": date.today() - timedelta(days=1),
            "end_date": date.today() + timedelta(days=2),
            "start_time": 1,  # 12:00 AM
            "end_time": 2,  # 12:30 AM
            "error_message": "Start date can&#39;t be a date in the past.",
        },
        {
            "title": "Test Event",
            "event_type": 1,  # Appearance or Signing
            "category": 1,  # Auto, Boat & Air
            "venue_name": "The Kimmel Center",
            "address": "300 S. Broad St",
            "city": "Philadelphia",
            "state": 39,  # pennsylvania
            "zip_code": "19102",
            "start_date": date.today() + timedelta(days=1),
            "end_date": date.today() - timedelta(days=2),
            "start_time": 1,  # 12:00 AM
            "end_time": 2,  # 12:30 AM
            "error_message": "End date must be on or after start date.",
        },
        {
            "title": "Test Event",
            "event_type": 1,  # Appearance or Signing
            "category": 1,  # Auto, Boat & Air
            "venue_name": "The Kimmel Center",
            "address": "300 S. Broad St",
            "city": "Philadelphia",
            "state": 0,  # didn't select a state
            "zip_code": "19102",
            "start_date": date.today(),
            "end_date": date.today() + timedelta(days=2),
            "start_time": 1,  # 12:00 AM
            "end_time": 2,  # 12:30 AM
            "error_message": "Start time can&#39;t be in the past.",
        },
        {
            "title": "Test Event",
            "event_type": 1,  # Appearance or Signing
            "category": 0,  # didn't select anything
            "venue_name": "The Kimmel Center",
            "address": "300 S. Broad St",
            "city": "Philadelphia",
            "state": 39,  # pennsylvania
            "zip_code": "19102",
            "start_date": date.today(),
            "end_date": date.today(),
            "start_time": 2,  # 12:00 AM
            "end_time": 1,  # 12:30 AM
            "error_message": "End time must be after start time.",
        },
    ]
    VALID_PACKAGE_DATA = {
        "name": "Test Package",
        "price": 1000,
        "audience": 2,  # 1-50
        "description": "The best package",
        "available_packages": 10,
        "package_type": 1,  # cash
    }
    INVALID_PACKAGE_DATA = [
        {
            "name": "Test Package",
            "price": 1000,
            "audience": 1,  # nothing selected
            "description": "The best package",
            "available_packages": 10,
            "package_type": 1,  # cash
            "error_message": "Please choose the audience reached.",
        },
        {
            "name": "Test Package" * 10,
            "price": 1000,
            "audience": 1,  # nothing selected
            "description": "The best package",
            "available_packages": 10,
            "package_type": 1,  # cash
            "error_message": "Field must be between 1 and 64 characters long.",
        },
        {
            "name": "Test Package" * 10,
            "price": 0,
            "audience": 1,  # nothing selected
            "description": "The best package",
            "available_packages": 10,
            "package_type": 1,  # cash
            "error_message": "Number must be between 1 and 2147483647.",
        },
        {
            "name": "Test Package" * 10,
            "price": 3147483647,
            "audience": 1,  # nothing selected
            "description": "The best package",
            "available_packages": 10,
            "package_type": 1,  # cash
            "error_message": "Number must be between 1 and 2147483647.",
        },
        {
            "name": "Test Package" * 10,
            "price": 2999,
            "audience": 1,  # nothing selected
            "description": "The best package",
            "available_packages": 0,
            "package_type": 1,  # cash
            "error_message": "Number must be between 1 and 2147483647.",
        },
        {
            "name": "Test Package" * 10,
            "price": 2999,
            "audience": 1,  # nothing selected
            "description": "The best package",
            "available_packages": 3147483647,
            "package_type": 1,  # cash
            "error_message": "Number must be between 1 and 2147483647.",
        },
    ]
    # numbers here are arbitrary
    ADMIN_ROUTES = ["/edit_profile/1", "/admin_panel/sponsor"]
    # numbers here are arbitrary
    SPONSOR_ROUTES = [
        "/saved_events",
        "/sponsorships/all",
        "/events/1/sponsorships/purchase",
    ]
    # numbers here are arbitrary
    ORGANIZER_ROUTES = [
        "/events/create",
        "/events/1/basic_info",
        "/events/1/event_details",
        "/events/1/demographics",
        "/events/1/packages",
        "/events/1/packages/1/edit",
        "/events/1/media",
        "/events/all",
    ]


class TestModelFactory:
    """Class to return instances of models needed for testing."""

    @classmethod
    def create_user(
        cls,
        password="password",
        email="greg@gmail.com",
        company="ABC Corp",
        has_paid=True,
        profile_photo_path=None,
    ):
        """Return an instance of the User class."""
        user = User(
            first_name="Greg",
            last_name="Smith",
            company=company,
            email=email,
            password=password,
            has_paid=has_paid,
            profile_photo_path=profile_photo_path,
        )
        return user

    @classmethod
    def create_role(cls, role_name):
        """Return an instance of the role class."""
        role_names = {
            "Event Organizer": [Permission.CREATE_EVENT],
            "Sponsor": [Permission.SPONSOR_EVENT],
            "Administrator": [
                Permission.CREATE_EVENT,
                Permission.SPONSOR_EVENT,
                Permission.ADMIN,
            ],
        }
        role = Role(name=role_name, permissions=sum(role_names[role_name]))
        return role

    @classmethod
    def create_event(
        cls, title, status, event_type="Conference", event_category="Music", id=None
    ):
        """Return an instance of the Event class."""
        event = Event(
            title=title,
            description="The best description ever",
            event_type=EventType(name=event_type),
            event_category=EventCategory(name=event_category),
        )
        if status.lower() in EventStatus.LIVE:
            event.published = True
            event.start_datetime = datetime.now()
            event.end_datetime = datetime.now() + timedelta(days=1)
        elif status.lower() == EventStatus.PAST:
            event.published = True
            event.start_datetime = datetime.now() - timedelta(days=3)
            event.end_datetime = datetime.now() - timedelta(days=1)
        elif status.lower() == EventStatus.DRAFT:
            event.published = False
            start_datetime = (datetime.now(),)
            end_datetime = datetime.now() + timedelta(days=1)
        if (
            id is not None
        ):  # used for elasticsearch tests where the model isn't added to the db
            event.id = id
        return event

    @classmethod
    def create_venue(cls, address="25 Ford Ave"):
        """Return an instance of the Venue class."""
        venue = Venue(
            name="ABC Venue",
            address=address,
            city="Scottsdale",
            state="AZ",
            zip_code="12345",
        )
        return venue

    @classmethod
    def create_package(cls, price=1000, available_packages=10):
        """Return an instance of the Package class."""
        package = Package(
            name="Social Media Package",
            price=price,
            audience="50-100",
            available_packages=available_packages,
            package_type="Cash",
        )
        return package

    @classmethod
    def create_sponsorship(cls, status):
        """Return an instance of the sponsorship class."""
        sponsorship = Sponsorship()
        if status.lower() in (SponsorshipStatus.CURRENT, SponsorshipStatus.PAST):
            sponsorship.timestamp = datetime.now()
            sponsorship.confirmation_code = str(uuid.uuid4())
        return sponsorship

    @classmethod
    def create_image(cls, path, image_type):
        """Return an instance of the Image class."""
        image = Image(path=path, image_type=image_type)
        return image
