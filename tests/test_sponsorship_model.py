import unittest
import uuid
from datetime import datetime
from .testing_data import TestModelFactory
from app import create_app, db
from app.models import Sponsorship


class SponsorshipModelTestCase(unittest.TestCase):
    """Class to test the Sponsorship Model."""

    def setUp(self):
        """Create application instance and insert necessary
        information into the database before each test.
        """
        self.app = create_app("testing")
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
        self.assertFalse(sponsorship.is_pending())

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
        self.assertFalse(sponsorship.is_pending())

    def test_sponsorship_is_pending_instance_method(self):
        """Test to ensure that a sponsorship without a confirmation code
        and timestamp is recognized as pending.
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
        sponsorship = TestModelFactory.create_sponsorship(status="pending")
        sponsorship.sponsor = user
        sponsorship.package = package
        sponsorship.event = event
        db.session.add_all([user, event, package, sponsorship])
        db.session.commit()

        self.assertFalse(sponsorship.is_current())
        self.assertFalse(sponsorship.is_past())
        self.assertTrue(sponsorship.is_pending())

    def test_sponsorship_is_pending_hybrid_expressions(self):
        """Test to ensure that the SQLAlchemy hybrid method
        decorator is functioning correctly when used in database queries.
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
        sponsorship = TestModelFactory.create_sponsorship(status="pending")
        sponsorship.sponsor = user
        sponsorship.package = package
        sponsorship.event = event
        db.session.add_all([user, event, package, sponsorship])
        db.session.commit()

        query_obj = Sponsorship.query.filter(Sponsorship.is_pending() == True).first()
        self.assertIsNotNone(query_obj)
        self.assertEqual(sponsorship, query_obj)

        # update the sponsorship obejct so it is not pending and check that the query returns null
        sponsorship.timestamp = datetime.now()
        sponsorship.confirmation_code = str(uuid.uuid4())
        db.session.commit()
        query_obj = Sponsorship.query.filter(Sponsorship.is_pending() == True).first()

        self.assertIsNone(query_obj)


if __name__ == "__main__":
    unittest.main()
