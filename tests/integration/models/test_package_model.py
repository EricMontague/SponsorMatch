"""This module contains tests for the package model."""


import unittest
from tests.integration.testing_data import TestModelFactory
from app import create_app
from app.extensions import db


class PackageModelTestCase(unittest.TestCase):
    """Class to test the Package Model."""

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

    def test_package_sold_out(self):
        """Test to ensure that a package is correctly
        recognized as sold out.
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

        package.num_purchased = package.available_packages
        self.assertTrue(package.is_sold_out())

    def test_package_num_sales(self):
        """Test to ensure that the number of packages purchased
        is recorded correctly in the database.
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

        self.assertEqual(package.num_for_sale(), 10)
        package.num_purchased += 1
        self.assertEqual(package.num_for_sale(), 9)


if __name__ == "__main__":
    unittest.main()
