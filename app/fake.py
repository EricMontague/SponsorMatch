"""This module is used for development purposes only.
It is to be used to generate fake user data for the
application.
"""
import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from faker import Faker
from app.main.forms import PEOPLE_RANGES, TIMES, TIME_FORMAT
from app import db
from app.models import (
    User,
    Role,
    Event,
    EventCategory,
    EventType,
    Venue,
    Package,
    ImageType,
    Sponsorship,
)


class FakeDataGenerator:
    """Class to generate fake data for the application."""

    def __init__(
        self, num_users, num_events, packages_per_event=4, sponsors_per_event=3
    ):
        self.faker = Faker()
        self.num_users = num_users
        self.num_events = num_events
        self.packages_per_event = packages_per_event
        self.sponsors_per_event = sponsors_per_event

    def add_all(self, reset_db=False):
        """Create all necessary tables and create all resources."""
        if reset_db:
            db.drop_all()
            db.create_all()
            EventCategory.insert_event_categories()
            EventType.insert_event_types()
            Role.insert_roles()
            ImageType.insert_image_types()
        self.add_users()
        self.add_events()
        self.add_packages()
        self.add_sponsorships()
        Event.reindex()  # makes sure that all event data is uploaded to Elasticsearch

    def add_users(self):
        """Add fake user data to the database."""
        i = 0
        while i < self.num_users:
            role = Role.query.filter_by(
                name=random.choice(["Event Organizer", "Sponsor"])
            ).first()
            user = User(
                first_name=self.faker.first_name(),
                last_name=self.faker.last_name(),
                company=self.faker.company(),
                email=self.faker.email(),
                password="password",
                has_paid=True,
                job_title=self.faker.job(),
                website=self.faker.url(),
                about=self.faker.text(),
                role=role,
            )
            db.session.add(user)
            try:
                db.session.commit()
                i += 1
            except IntegrityError:  # the unique constraint was violated
                db.session.rollback()

    def add_events(self):
        """Add fake event data to the database."""
        user_count = User.query.count()
        category_count = EventCategory.query.count()
        type_count = EventType.query.count()
        role = Role.query.filter_by(name="Event Organizer").first()
        users = User.query.filter_by(role=role).all()
        for index in range(self.num_events):
            user = random.choice(users)
            event_category = EventCategory.query.get(random.randint(1, category_count))
            event_type = EventType.query.get(random.randint(1, type_count))
            venue = Venue(
                name=self.faker.company(),
                address=self.faker.street_address(),
                city=self.faker.city(),
                state=self.faker.state(),
                zip_code=self.faker.zipcode(),
            )
            start_date = self.faker.date_between(
                start_date=datetime.now() + timedelta(days=1), end_date="+30d"
            )
            string_time = random.choice(TIMES[:40])[1]
            start_time = datetime.strptime(string_time, TIME_FORMAT)
            start_datetime = datetime.combine(start_date, start_time.time())
            event = Event(
                title=self.faker.company() + random.choice([" Party", " Gala"]),
                start_datetime=start_datetime,
                end_datetime=start_datetime + timedelta(days=1),
                attendees=random.choice(PEOPLE_RANGES[1:])[1],
                male_to_female="50-50",
                description=self.faker.text(),
                pitch=self.faker.text(),
                published=True,
                user=user,
                venue=venue,
                event_type=event_type,
                event_category=event_category,
            )

            db.session.add(event)
        db.session.commit()

    def add_packages(self):
        """Add fake package data to the database."""
        event_count = Event.query.count()
        for count in range(1, event_count + 1):
            event = Event.query.get(count)
            for num in range(self.packages_per_event):
                package = Package(
                    name=self.faker.color_name() + " Package",
                    price=self.faker.pydecimal(
                        left_digits=5, right_digits=2, positive=True, min_value=1.0
                    ),
                    audience=random.choice(PEOPLE_RANGES[1:])[1],
                    description=self.faker.text(),
                    available_packages=self.faker.pyint(
                        min_value=1, max_value=20, step=1
                    ),
                    package_type=random.choice(["Cash", "In-Kind"]),
                    event=event,
                )
                db.session.add(package)
        db.session.commit()

    def add_sponsorships(self):
        """Add fake sponsorship deals to the database."""
        event_count = Event.query.count()
        role = Role.query.filter_by(name="Sponsor").first()
        users = User.query.filter_by(role=role).all()
        for count in range(1, event_count + 1):
            event = Event.query.get(count)
            packages = event.packages.all()
            i = 0
            while i < self.sponsors_per_event:
                user = random.choice(users)
                try:
                    sponsorship = Sponsorship(
                        event=event,
                        sponsor=user,
                        package=random.choice(packages),
                        timestamp=datetime.now(),
                        confirmation_code=str(uuid.uuid4()),
                    )
                    db.session.add(sponsorship)
                    db.session.commit()
                    i += 1
                except IntegrityError:  # a user can't buy the same package twice
                    db.session.rollback()
