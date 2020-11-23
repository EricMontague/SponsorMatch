"""This module is used for development purposes only.
It is to be used to generate fake user data for the
application.
"""
import os
import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from faker import Faker
from app.forms import PEOPLE_RANGES, TIMES, TIME_FORMAT
# from app.search import sqlalchemy_search_middleware
from app.extensions import db
from app.models import (
    User,
    Role,
    Event,
    EventCategory,
    EventType,
    Venue,
    Package,
    ImageType,
    Image,
    Sponsorship,
)


DEFAULT_EVENT_IMAGE_DIR = "/app/static/images/default_event_images"


class FakeDataGenerator:
    """Class to generate fake data for the application."""

    def __init__(
        self,
        num_users,
        num_events,
        packages_per_event=4,
        sponsors_per_event=3,
        event_image_directory="",
    ):
        self.faker = Faker()
        self.num_users = num_users
        self.num_events = num_events
        self.packages_per_event = packages_per_event
        self.sponsors_per_event = sponsors_per_event
        self.event_image_directory = event_image_directory or os.path.join(
            os.getcwd() + DEFAULT_EVENT_IMAGE_DIR
        )

    def add_all(self):
        """Create all necessary tables and create all resources."""
        print("Generating fake data...")
        self.add_users()
        self.add_events()
        self.add_packages()
        self.add_sponsorships()
        print("Indexing Elasticsearch data...")
        # makes sure that all event data is uploaded to Elasticsearch
        print("Done!")

    def add_users(self):
        """Add fake user data to the database."""
        print("Adding users...")
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
        print("Add events...")
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
                start_date=datetime.now() + timedelta(days=random.randint(1, 365)),
                end_date="+30d",
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
            image = self.get_random_event_image(event)
            event.image = image
            db.session.add(event)
        db.session.commit()

    def add_packages(self):
        """Add fake package data to the database."""
        print("Adding packages...")
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
        print("Adding sponsorships...")
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

    def get_random_event_image(self, event):
        """Return a random event image from the default images
        directory.
        """
        filename = random.choice(os.listdir(self.event_image_directory))
        filepath = self.event_image_directory + "/" + filename
        image = Image.query.filter_by(path=filepath).first()
        if image is None:
            image = Image(
                path=filepath,
                event=event,
                image_type=ImageType.query.filter_by(name="Main Event Image").first(),
            )
            db.session.add(image)
            db.session.commit()
        print(f"Image is: {image}")
        return image
