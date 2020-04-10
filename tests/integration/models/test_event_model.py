"""This module contains tests for the event model."""


import unittest
import uuid
from datetime import datetime, timedelta, date, time
from app import create_app
from app.extensions import db
from tests.integration.testing_data import TestModelFactory
from app.models import ImageType, Event


class EventModelTestCase(unittest.TestCase):
    """Class to run tests on the event model."""

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

    def test_event_is_ongoing_instance_method(self):
        """Test that an event that is ongoing is being
        recognize as such.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "live")
        event.user = user
        event.venue = venue
        db.session.add_all([user, event])
        db.session.commit()

        self.assertTrue(event.is_ongoing())
        self.assertFalse(event.has_ended())
        self.assertFalse(event.is_draft())

    def test_event_is_ongoing_expression(self):
        """Test to ensure that the is_ongoing() method
        is functioning correctly within SQLAlchemy queries.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "live")
        event.user = user
        event.venue = venue
        db.session.add_all([user, event])
        db.session.commit()

        query_obj = Event.query.filter(Event.is_ongoing() == True).first()
        self.assertIsNotNone(query_obj)
        self.assertEqual(event, query_obj)

    def test_event_has_ended_instance_method(self):
        """Test to ensure that an event is correctly
        reporting that it has ended.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "past")
        event.user = user
        event.venue = venue
        db.session.add_all([user, event])
        db.session.commit()

        self.assertFalse(event.is_ongoing())
        self.assertTrue(event.has_ended())
        self.assertFalse(event.is_draft())

    def test_event_has_ended_expression(self):
        """Test to ensure the correct functionality of
        the has_ended() method in a SQLAlchemy query.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "past")
        event.user = user
        event.venue = venue
        db.session.add_all([user, event])
        db.session.commit()

        result = Event.query.filter(Event.has_ended() == True).first()
        self.assertIsNotNone(result)
        self.assertEqual(event, result)

    def test_event_is_draft(self):
        """Test to ensure that an event is correctly
        reporting that it is in draft status.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "draft")
        event.user = user
        event.venue = venue
        db.session.add_all([user, event])
        db.session.commit()

        self.assertFalse(event.is_ongoing())
        self.assertFalse(event.has_ended())
        self.assertTrue(event.is_draft())

    def test_start_date_method(self):
        """Test to ensure correct functionality of
        the start_date() method.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "draft")
        event.user = user
        event.venue = venue
        event.start_datetime = datetime(2020, 2, 9, 12, 12, 12)
        event.end_datetime = datetime(2020, 2, 10, 12, 12, 12)
        db.session.add_all([user, event])
        db.session.commit()

        # return datetime object with no arguments passed in
        date_obj = event.start_date()
        self.assertIsInstance(date_obj, date)
        self.assertEqual(date_obj, date(2020, 2, 9))

        date_string = event.start_date("%a, %b %-d")
        self.assertIsInstance(date_string, str)
        self.assertEqual(date_string, "Sun, Feb 9")
        self.assertNotEqual(date_string, "Sunday, Feb 9")

        # should have no leading zero
        self.assertNotEqual(date_string, "Sun, Feb 09")

        # should have the comma in the output
        self.assertNotEqual(date_string, "Sun Feb 9")

        # should have spaces in the output
        self.assertNotEqual(date_string, "SunFeb 9")

        # should be capitalized
        self.assertNotEqual(date_string, "sun feb 9")

        # other invalid input
        date_string = event.start_date("foobar")
        self.assertIsInstance(date_string, str)
        self.assertEqual(date_string, "foobar")

        with self.assertRaises(TypeError):
            event.start_date(2200)

        with self.assertRaises(TypeError):
            event.start_date(12.456)

        with self.assertRaises(TypeError):
            event.start_date([1, 2, 3])

        with self.assertRaises(TypeError):
            event.start_date({"a": 1})

        with self.assertRaises(TypeError):
            event.start_date({1, 2, 3})

        with self.assertRaises(TypeError):
            event.start_date((1, 2, 3))

        with self.assertRaises(TypeError):
            event.start_date(user)

    def test_end_date_method(self):
        """Test to ensure correct functionality of
        the end_date() method.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "draft")
        event.user = user
        event.venue = venue
        event.start_datetime = datetime(2020, 2, 8, 12, 12, 12)
        event.end_datetime = datetime(2020, 2, 9, 12, 12, 12)
        db.session.add_all([user, event])
        db.session.commit()

        # return datetime object with no arguments passed in
        date_obj = event.end_date()
        self.assertIsInstance(date_obj, date)
        self.assertEqual(date_obj, date(2020, 2, 9))

        date_string = event.end_date("%a, %b %-d")
        self.assertIsInstance(date_string, str)
        self.assertEqual(date_string, "Sun, Feb 9")
        self.assertNotEqual(date_string, "Sunday, Feb 9")

        # should have no leading zero
        self.assertNotEqual(date_string, "Sun, Feb 09")

        # should have the comma in the output
        self.assertNotEqual(date_string, "Sun Feb 9")

        # should have spaces in the output
        self.assertNotEqual(date_string, "SunFeb 9")

        # should be capitalized
        self.assertNotEqual(date_string, "sun feb 9")

        # other invalid input
        date_string = event.end_date("foobar")
        self.assertIsInstance(date_string, str)
        self.assertEqual(date_string, "foobar")

        with self.assertRaises(TypeError):
            event.start_date(2200)

        with self.assertRaises(TypeError):
            event.start_date(12.456)

        with self.assertRaises(TypeError):
            event.start_date([1, 2, 3])

        with self.assertRaises(TypeError):
            event.start_date({"a": 1})

        with self.assertRaises(TypeError):
            event.start_date({1, 2, 3})

        with self.assertRaises(TypeError):
            event.start_date((1, 2, 3))

        with self.assertRaises(TypeError):
            event.start_date(user)

    def test_start_time_method(self):
        """Test to ensure correct functionality of
        the start_time() method.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "draft")
        event.user = user
        event.venue = venue
        event.start_datetime = datetime(2020, 2, 9, 9, 12, 12)
        event.end_datetime = datetime(2020, 2, 9, 12, 12, 12)
        db.session.add_all([user, event])
        db.session.commit()

        time_obj = event.start_time()
        self.assertIsInstance(time_obj, time)
        self.assertEqual(time_obj, time(9, 12, 12))

        time_string = event.start_time("%-I:%M %p")
        self.assertIsInstance(time_string, str)
        self.assertEqual(time_string, "9:12 AM")

        # check for different spacing
        self.assertNotEqual(time_string, "9: 12 AM")

        # check that colon is there
        self.assertNotEqual(time_string, "912 AM")

        # no leading zero should be there
        self.assertNotEqual(time_string, "09:12 AM")

        # other invalid input
        time_string = event.start_time("foobar")
        self.assertIsInstance(time_string, str)
        self.assertEqual(time_string, "foobar")

        with self.assertRaises(TypeError):
            event.start_time(2200)

        with self.assertRaises(TypeError):
            event.start_time(12.456)

        with self.assertRaises(TypeError):
            event.start_time([1, 2, 3])

        with self.assertRaises(TypeError):
            event.start_time({"a": 1})

        with self.assertRaises(TypeError):
            event.start_time({1, 2, 3})

        with self.assertRaises(TypeError):
            event.start_time((1, 2, 3))

        with self.assertRaises(TypeError):
            event.start_time(user)

    def test_end_time_method(self):
        """Test to ensure correct functionality of
        the end_time() method.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "draft")
        event.user = user
        event.venue = venue
        event.start_datetime = datetime(2020, 2, 8, 7, 12, 12)
        event.end_datetime = datetime(2020, 2, 9, 9, 12, 12)
        db.session.add_all([user, event])
        db.session.commit()

        time_obj = event.end_time()
        self.assertIsInstance(time_obj, time)
        self.assertEqual(time_obj, time(9, 12, 12))

        time_string = event.end_time("%-I:%M %p")
        self.assertIsInstance(time_string, str)
        self.assertEqual(time_string, "9:12 AM")

        # check for different spacing
        self.assertNotEqual(time_string, "9: 12 AM")

        # check that colon is there
        self.assertNotEqual(time_string, "912 AM")

        # no leading zero should be there
        self.assertNotEqual(time_string, "09:12 AM")

        # other invalid input
        time_string = event.end_time("foobar")
        self.assertIsInstance(time_string, str)
        self.assertEqual(time_string, "foobar")

        with self.assertRaises(TypeError):
            event.end_time(2200)

        with self.assertRaises(TypeError):
            event.end_time(12.456)

        with self.assertRaises(TypeError):
            event.end_time([1, 2, 3])

        with self.assertRaises(TypeError):
            event.end_time({"a": 1})

        with self.assertRaises(TypeError):
            event.end_time({1, 2, 3})

        with self.assertRaises(TypeError):
            event.end_time((1, 2, 3))

        with self.assertRaises(TypeError):
            event.end_time(user)

    def test_total_sales(self):
        """Test to ensure that an event is reporting
        the correct total sales numbers.
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
        db.session.add_all([user, event, package])
        db.session.commit()

        self.assertEqual(event.total_sales(), 0)

        package.num_purchased += 1

        self.assertEqual(event.total_sales(), 100)

    def test_num_packages_sold(self):
        """Test to ensure that an event is reporting the correct
        number of packages sold.
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
        db.session.add_all([user, event, package])
        db.session.commit()

        self.assertEqual(event.num_packages_sold(), 0)
        package.num_purchased += 1
        self.assertEqual(event.num_packages_sold(), 1)

    def test_num_packages_available(self):
        """Test that an event is reporting the correct number
        of packages available. These are the total number of
        packages that the event originally starts with.
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
        db.session.add_all([user, event, package])
        db.session.commit()

        self.assertEqual(event.num_packages_available(), 10)

    def test_price_range(self):
        """Test that an event is reporting the correct price range."""
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "live")
        event.user = user
        event.venue = venue
        package_one = TestModelFactory.create_package(price=100, available_packages=10)
        package_two = TestModelFactory.create_package(price=2000, available_packages=10)
        package_one.event = event
        package_two.event = event
        db.session.add_all([user, event, package_one, package_two])
        db.session.commit()

        price_range = event.price_range()
        low_and_high = price_range.split(" - ")
        self.assertEqual(low_and_high[0], "$100")
        self.assertEqual(low_and_high[1], "$2000")

    def test_get_main_image(self):
        """Test to ensure that the main_image property
        returns paths in the correct format.
        """
        path = "/Users/ericmontague/sponsormatch/app/static/images/test_image.jpg"
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "live")
        event.user = user
        event.venue = venue
        package = TestModelFactory.create_package(price=100, available_packages=10)
        package.event = event
        image_type = ImageType(name="Main Event Image")
        db.session.add_all([user, event, package, image_type])
        db.session.commit()

        image_type = ImageType.query.get(1)
        image = TestModelFactory.create_image(path=path, image_type=image_type)
        image.event = event

        image_path = event.main_image
        self.assertEqual(image_path, "images/test_image.jpg")

    def test_get_misc_images(self):
        """Test to ensure that the misc_images property
        returns images in the correct format.
        """
        path_one = (
            "/Users/ericmontague/sponsormatch/app/static/images/test_image_one.jpg"
        )
        path_two = (
            "/Users/ericmontague/sponsormatch/app/static/images/test_image_two.jpg"
        )
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()

        event = TestModelFactory.create_event("Test Event", "live")
        event.user = user
        event.venue = venue
        package = TestModelFactory.create_package(price=100, available_packages=10)
        package.event = event
        image_type = ImageType(name="Misc")
        db.session.add_all([user, event, package, image_type])
        db.session.commit()

        image_type = ImageType.query.get(1)
        image_one = TestModelFactory.create_image(path=path_one, image_type=image_type)
        image_two = TestModelFactory.create_image(path=path_two, image_type=image_type)
        image_one.event = event
        image_two.event = event
        db.session.commit()

        paths = event.misc_images
        self.assertEqual(paths[0], "images/test_image_one.jpg")
        self.assertEqual(paths[1], "images/test_image_two.jpg")

    def test_num_sponsors(self):
        """Test that an event is reporting the correct
        number of sponsors it has.
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

        self.assertEqual(event.num_sponsors(), 1)


if __name__ == "__main__":
    unittest.main()
