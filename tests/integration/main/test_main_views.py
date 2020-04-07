"""This module contains tests for the view functions in the main blueprint."""


import unittest
from datetime import datetime, timedelta
from integration.testing_data import ViewFunctionTestData, TestModelFactory
from app import create_app
from app.extensions import db
from app.models import User, Role, Event, EventType, EventCategory, Venue, Package


#need to put some of these tests in the events folder instead since I changed
#the project structure around
class MainViewsTestCase(unittest.TestCase):
    """Class to test view functions in the main blueprint."""

    def setUp(self):
        """Create application instance and insert necessary
        information into the database before each test.
        """
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

    def tearDown(self):
        """Pop application context, remove the db session,
        and drop all tables in the database.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        """Test the index view function when not logged in."""

        # send GET request
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

        # test for text in the navbar and navbar dropdown
        self.assertTrue("SponsorMatch" in response.get_data(as_text=True))
        self.assertTrue("Stranger!" in response.get_data(as_text=True))
        self.assertTrue("Sign In" in response.get_data(as_text=True))
        self.assertTrue("Sign Up" in response.get_data(as_text=True))
        self.assertFalse("Account" in response.get_data(as_text=True))
        self.assertFalse("Settings" in response.get_data(as_text=True))
        self.assertFalse("Log Out" in response.get_data(as_text=True))

    def test_page_not_found(self):
        """Test that the Page not Found template is returned
        when a user sends a request to a route that doesn't exist.
        """
        response = self.client.get("/foobar")
        self.assertEqual(response.status_code, 404)
        self.assertTrue("Page Not Found" in response.get_data(as_text=True))

    def test_create_event_valid_input(self):
        """Test sending valid inputs to the create event view function."""
        # create user
        EventType.insert_event_types()
        EventCategory.insert_event_categories()
        role = Role.query.filter_by(name="Event Organizer").first()
        user = TestModelFactory.create_user(password="password")
        user.role = role
        db.session.add(user)
        db.session.commit()

        # Should be redirected if not logged in
        response = self.client.get("/events/create", follow_redirects=True)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(
            "Please log in to access this page" in response.get_data(as_text=True)
        )

        with self.client:
            # log the user in
            response = self.client.post(
                "/auth/login",
                data={"email": user.email, "password": "password"},
                follow_redirects=True,
            )

            # GET request should be successful
            response = self.client.get("/events/create", follow_redirects=True)
            self.assertTrue(response.status_code, 200)
            self.assertTrue("Basic Info" in response.get_data(as_text=True))
            self.assertTrue("Location" in response.get_data(as_text=True))
            self.assertTrue("Date and Time" in response.get_data(as_text=True))

            # POST request should be successful
            response = self.client.post(
                "/events/create",
                data={
                    "title": ViewFunctionTestData.VALID_EVENT_DATA["title"],
                    "event_type": ViewFunctionTestData.VALID_EVENT_DATA["event_type"],
                    "category": ViewFunctionTestData.VALID_EVENT_DATA["category"],
                    "venue_name": ViewFunctionTestData.VALID_EVENT_DATA["venue_name"],
                    "address": ViewFunctionTestData.VALID_EVENT_DATA["address"],
                    "city": ViewFunctionTestData.VALID_EVENT_DATA["city"],
                    "state": ViewFunctionTestData.VALID_EVENT_DATA["state"],
                    "zip_code": ViewFunctionTestData.VALID_EVENT_DATA["zip_code"],
                    "start_date": ViewFunctionTestData.VALID_EVENT_DATA["start_date"],
                    "end_date": ViewFunctionTestData.VALID_EVENT_DATA["end_date"],
                    "start_time": ViewFunctionTestData.VALID_EVENT_DATA["start_time"],
                    "end_time": ViewFunctionTestData.VALID_EVENT_DATA["end_time"],
                },
                follow_redirects=True,
            )
            self.assertEqual(response.status_code, 200)

            # sidebar text
            self.assertTrue("Basic Info" in response.get_data(as_text=True))
            self.assertTrue("Event Details" in response.get_data(as_text=True))
            self.assertTrue("Demographics" in response.get_data(as_text=True))
            self.assertTrue("Media" in response.get_data(as_text=True))
            self.assertTrue("Packages" in response.get_data(as_text=True))

            # form headers
            self.assertTrue("Main Event Image" in response.get_data(as_text=True))
            self.assertTrue("Description & Pitch" in response.get_data(as_text=True))

        # check that event was created
        event = Event.query.get(1)
        self.assertIsNotNone(event)
        self.assertEqual(event.title, ViewFunctionTestData.VALID_EVENT_DATA["title"])
        self.assertEqual(
            event.venue.name, ViewFunctionTestData.VALID_EVENT_DATA["venue_name"]
        )
        self.assertEqual(event.user, user)
        self.assertFalse(
            event.published
        )  # published attribute should be defaulted to False

    def test_create_event_invalid_input(self):
        """Test sending invalid input to the create event view function."""
        EventType.insert_event_types()
        EventCategory.insert_event_categories()
        role = Role.query.filter_by(name="Event Organizer").first()
        user = TestModelFactory.create_user(password="password")
        user.role = role
        db.session.add(user)
        db.session.commit()

        # Should be redirected if not logged in
        response = self.client.get("/events/create", follow_redirects=True)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(
            "Please log in to access this page" in response.get_data(as_text=True)
        )

        with self.client:
            # log the user in
            response = self.client.post(
                "/auth/login",
                data={"email": user.email, "password": "password"},
                follow_redirects=True,
            )

            for data in ViewFunctionTestData.INVALID_EVENT_DATA:
                with self.subTest(data=data):
                    response = self.client.post(
                        "/events/create",
                        data={
                            "title": data["title"],
                            "event_type": data["event_type"],
                            "category": data["category"],
                            "venue_name": data["venue_name"],
                            "address": data["address"],
                            "city": data["city"],
                            "state": data["state"],
                            "zip_code": data["zip_code"],
                            "start_date": data["start_date"],
                            "end_date": data["end_date"],
                            "start_time": data["start_time"],
                            "end_time": data["end_time"],
                        },
                        follow_redirects=True,
                    )
                    self.assertTrue(
                        data["error_message"] in response.get_data(as_text=True)
                    )
        self.assertIsNone(user.events.first())

    def test_delete_event(self):
        """Test for the delete event view function."""
        role = Role.query.filter_by(name="Event Organizer").first()
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "live")
        event.user = user
        event.venue = venue
        db.session.add_all([user, event])
        db.session.commit()

        # Should be redirected if not logged in
        response = self.client.post(f"/events/{event.id}/delete", follow_redirects=True)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(
            "Please log in to access this page" in response.get_data(as_text=True)
        )

        with self.client:
            # log in
            response = self.client.post(
                "/auth/login",
                data={"email": user.email, "password": "password"},
                follow_redirects=True,
            )

            response = self.client.post(
                f"/events/{event.id}/delete", follow_redirects=True
            )
            self.assertTrue(response.status_code, 200)

            self.assertIsNotNone(response.json)
            self.assertEqual(
                response.json["message"], "Your event has been successfully deleted."
            )

        event = Event.query.get(1)
        self.assertIsNone(event)
        self.assertIsNone(user.events.first())

    def test_packages_valid_input(self):
        """Test sending valid input to the packages
        view function.
        """
        role = Role.query.filter_by(name="Event Organizer").first()
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "live")
        event.user = user
        event.venue = venue
        db.session.add_all([user, event])
        db.session.commit()

        # Should be redirected if not logged in
        response = self.client.get(
            f"/events/{event.id}/packages", follow_redirects=True
        )
        self.assertTrue(response.status_code, 200)
        self.assertTrue(
            "Please log in to access this page" in response.get_data(as_text=True)
        )

        with self.client:
            # log in
            response = self.client.post(
                "/auth/login",
                data={"email": user.email, "password": "password"},
                follow_redirects=True,
            )

            # send GET request
            response = self.client.get(
                f"/events/{event.id}/packages", follow_redirects=True
            )
            self.assertTrue(response.status_code, 200)
            self.assertTrue("Add your first package" in response.get_data(as_text=True))

            # sidebar text
            self.assertTrue("Basic Info" in response.get_data(as_text=True))
            self.assertTrue("Event Details" in response.get_data(as_text=True))
            self.assertTrue("Demographics" in response.get_data(as_text=True))
            self.assertTrue("Media" in response.get_data(as_text=True))
            self.assertTrue("Packages" in response.get_data(as_text=True))

            # send POST request
            response = self.client.post(
                f"/events/{event.id}/packages",
                data={
                    "name": ViewFunctionTestData.VALID_PACKAGE_DATA["name"],
                    "price": ViewFunctionTestData.VALID_PACKAGE_DATA["price"],
                    "audience": ViewFunctionTestData.VALID_PACKAGE_DATA[
                        "audience"
                    ],  # 1-50
                    "description": ViewFunctionTestData.VALID_PACKAGE_DATA[
                        "description"
                    ],
                    "available_packages": ViewFunctionTestData.VALID_PACKAGE_DATA[
                        "available_packages"
                    ],
                    "package_type": ViewFunctionTestData.VALID_PACKAGE_DATA[
                        "package_type"
                    ],  # cash
                },
                follow_redirects=True,
            )
            self.assertEqual(response.status_code, 200)
            self.assertFalse(
                "Add your first package" in response.get_data(as_text=True)
            )
            self.assertTrue("Publish" in response.get_data(as_text=True))
            self.assertTrue(
                ViewFunctionTestData.VALID_PACKAGE_DATA["name"]
                in response.get_data(as_text=True)
            )
            self.assertTrue(
                str(ViewFunctionTestData.VALID_PACKAGE_DATA["price"])
                in response.get_data(as_text=True)
            )
            self.assertTrue(
                str(ViewFunctionTestData.VALID_PACKAGE_DATA["available_packages"])
                in response.get_data(as_text=True)
            )

        package = Package.query.get(1)
        self.assertIsNotNone(package)
        self.assertIsNotNone(event.packages.first())
        self.assertEqual(package.name, ViewFunctionTestData.VALID_PACKAGE_DATA["name"])
        self.assertEqual(
            package.description, ViewFunctionTestData.VALID_PACKAGE_DATA["description"]
        )

    def test_packages_invalid_input(self):
        """Test sending invalid inputs to the packages view function."""
        role = Role.query.filter_by(name="Event Organizer").first()
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "live")
        event.user = user
        event.venue = venue
        db.session.add_all([user, event])
        db.session.commit()

        with self.client:
            # log in
            response = self.client.post(
                "/auth/login",
                data={"email": user.email, "password": "password"},
                follow_redirects=True,
            )

            for data in ViewFunctionTestData.INVALID_PACKAGE_DATA:
                with self.subTest(data=data):
                    response = self.client.post(
                        f"/events/{event.id}/packages",
                        data={
                            "name": data["name"],
                            "price": data["price"],
                            "audience": data["audience"],  # 1-50
                            "description": data["description"],
                            "available_packages": data["available_packages"],
                            "package_type": data["package_type"],  # cash
                        },
                        follow_redirects=True,
                    )
                    self.assertTrue(
                        data["error_message"] in response.get_data(as_text=True)
                    )
        self.assertIsNone(event.packages.first())

    def test_delete_package(self):
        """Test the delete package view function."""
        role = Role.query.filter_by(name="Event Organizer").first()
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

        # Should be redirected if not logged in
        response = self.client.post(
            f"/events/{event.id}/packages/{package.id}/delete", follow_redirects=True
        )
        self.assertTrue(response.status_code, 200)
        self.assertTrue(
            "Please log in to access this page" in response.get_data(as_text=True)
        )

        with self.client:
            # log in
            response = self.client.post(
                "/auth/login",
                data={"email": user.email, "password": "password"},
                follow_redirects=True,
            )

            # Get request shouldn't work
            response = self.client.get(
                f"/events/{event.id}/packages/{package.id}/delete",
                follow_redirects=True,
            )
            self.assertEqual(response.status_code, 405)
            self.assertTrue("Method Not Allowed" in response.get_data(as_text=True))

            # send POST request to delete package
            response = self.client.post(
                f"/events/{event.id}/packages/{package.id}/delete",
                follow_redirects=True,
            )
            self.assertTrue(response.status_code, 200)

            # this view return json data
            self.assertIsNotNone(response.json)
            self.assertEqual(response.json["url"], f"/events/{event.id}/packages")

        package = Package.query.get(1)
        self.assertIsNone(package)
        self.assertIsNone(event.packages.first())

    def test_view_event(self):
        """Test the event view function."""
        role = Role.query.filter_by(name="Event Organizer").first()
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

        with self.client:
            # log the user in
            response = self.client.post(
                "/auth/login",
                data={"email": user.email, "password": "password"},
                follow_redirects=True,
            )

            # GET request should be successful
            response = self.client.get(f"/events/{event.id}", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(event.title in response.get_data(as_text=True))
            self.assertTrue(user.company in response.get_data(as_text=True))
            self.assertTrue("Packages" in response.get_data(as_text=True))
            self.assertTrue(package.name in response.get_data(as_text=True))
            self.assertTrue(package.package_type in response.get_data(as_text=True))
            self.assertTrue("Contact" in response.get_data(as_text=True))
            self.assertTrue("Description" in response.get_data(as_text=True))
            self.assertTrue("Pitch" in response.get_data(as_text=True))
            self.assertTrue("Audience" in response.get_data(as_text=True))
            self.assertTrue("Date and Time" in response.get_data(as_text=True))
            self.assertTrue("Location" in response.get_data(as_text=True))
            self.assertTrue("Audience" in response.get_data(as_text=True))
            self.assertTrue("Edit Event" in response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
