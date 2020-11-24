"""This module contains tests for the sponsorship model."""


import unittest
import uuid
from datetime import datetime
from tests.integration.testing_data import TestModelFactory
from app import create_app
from app.extensions import db
from app.models import Sponsorship


class SponsorshipModelTestCase(unittest.TestCase):
    """Class to test the Sponsorship Model."""

    def setUp(self):
        """Create application instance and insert necessary
        information into the database before each test.
        """
        self.app = create_app("testing", False)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Pop application context, remove the db session,
        and drop all tables in the database.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_sponsorship_is_current(self):
        """Test to ensure that a sponsorsihp for an ongoing
        event is recognized as current.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "live")
        event.user = user
        event.venue = venue
        package = TestModelFactory.create_package(price=100, available_packages=10)
        package.event = event
        sponsorship = TestModelFactory.create_sponsorship(status="current")
        sponsorship.sponsor = user
        sponsorship.package = package
        sponsorship.event = event
        db.session.add_all([user, event, package, sponsorship])
        db.session.commit()

        self.assertTrue(sponsorship.is_current())
        self.assertFalse(sponsorship.is_past())

    def test_sponsorship_is_past(self):
        """Test to ensure that a sponsorship for an event that has ended
        is recognized as a past sponsorship.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "past")
        event.user = user
        event.venue = venue
        package = TestModelFactory.create_package(price=100, available_packages=10)
        package.event = event
        sponsorship = TestModelFactory.create_sponsorship(status="past")
        sponsorship.sponsor = user
        sponsorship.package = package
        sponsorship.event = event
        db.session.add_all([user, event, package, sponsorship])
        db.session.commit()

        self.assertFalse(sponsorship.is_current())
        self.assertTrue(sponsorship.is_past())

  
if __name__ == "__main__":
    unittest.main()
