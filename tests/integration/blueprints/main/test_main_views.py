"""This module contains tests for the view functions in the main blueprint."""


import unittest
from app import create_app
from app.extensions import db
from app.models import User, Role


class MainViewsTestCase(unittest.TestCase):
    """Class to test view functions in the main blueprint."""
        
    def setUp(self):
        """Create application instance and insert necessary
        information into the database before each test.
        """
        
        self.app = create_app("testing", False)
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
        self.assertTrue("Not Found" in response.get_data(as_text=True))

    

    

    

    

    

    

    


if __name__ == "__main__":
    unittest.main()
