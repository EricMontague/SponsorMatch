"""This module contains tests for the basic functionality and
setup of the app.
"""


import unittest
from flask import current_app
from app import create_app
from app.extensions import db


class BasicsTestCase(unittest.TestCase):
    """Class to run a basic test to make sure that the application is running."""

    # runs before each test
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    # runs after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        """Tests that the application instance is successfully
		created.
		"""
        self.assertTrue(current_app.config["TESTING"])

    def test_app_is_testing(self):
        """Tests whether the app is running with the testing
		configuration.
		"""
        self.assertTrue(current_app.config["TESTING"])


if __name__ == "__main__":
    unittest.main()
