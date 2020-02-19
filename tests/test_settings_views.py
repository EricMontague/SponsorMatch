import unittest
from .testing_data import ViewFunctionTestData, TestModelFactory
from app import create_app, db
from app.models import User, Role


class SettingsViewsTestCase(unittest.TestCase):
    """Class to test view functions in the settings blueprint."""

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

    def test_change_password_valid_input(self):
        """Test for senfing valid input to the change password view function."""
        role = Role.query.filter_by(name="Event Organizer").first()
        user = TestModelFactory.create_user(password="password")
        user.role = role
        db.session.add(user)
        db.session.commit()

        # Should be redirected if not logged in
        response = self.client.get("/settings/change_password", follow_redirects=True)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(
            "Please log in to access this page" in response.get_data(as_text=True)
        )

        # log the user in
        with self.client:
            response = self.client.post(
                "/auth/login",
                data={"email": user.email, "password": "password"},
                follow_redirects=True,
            )

            # send GET request
            response = self.client.get(
                "/settings/change_password", follow_redirects=True
            )
            self.assertTrue(response.status_code, 200)
            self.assertTrue("Account Information" in response.get_data(as_text=True))
            self.assertTrue("Change Password" in response.get_data(as_text=True))
            self.assertTrue("Change Email" in response.get_data(as_text=True))
            self.assertTrue("Change Your Password" in response.get_data(as_text=True))

            # send POST request
            response = self.client.post(
                "/settings/change_password",
                data={
                    "old_password": ViewFunctionTestData.VALID_CHANGE_PASSWORD_DATA[
                        "old_password"
                    ],
                    "new_password": ViewFunctionTestData.VALID_CHANGE_PASSWORD_DATA[
                        "new_password"
                    ],
                    "confirm_password": ViewFunctionTestData.VALID_CHANGE_PASSWORD_DATA[
                        "confirm_password"
                    ],
                },
                follow_redirects=True,
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(
                ViewFunctionTestData.VALID_CHANGE_PASSWORD_DATA["message"]
                in response.get_data(as_text=True)
            )

        self.assertTrue(
            user.verify_password(
                ViewFunctionTestData.VALID_CHANGE_PASSWORD_DATA["new_password"]
            )
        )

    def test_change_password_invalid_input(self):
        """Test for senfing invalid input to the change password view function."""
        role = Role.query.filter_by(name="Event Organizer").first()
        user = TestModelFactory.create_user(password="password")
        user.role = role
        db.session.add(user)
        db.session.commit()

        # log the user in
        with self.client:
            response = self.client.post(
                "/auth/login",
                data={"email": user.email, "password": "password"},
                follow_redirects=True,
            )

            for data in ViewFunctionTestData.INVALID_CHANGE_PASSWORD_DATA:
                with self.subTest(data=data):
                    response = self.client.post(
                        "/settings/change_password",
                        data={
                            "old_password": data["old_password"],
                            "new_password": data["new_password"],
                            "confirm_password": data["confirm_password"],
                        },
                        follow_redirects=True,
                    )
                    self.assertTrue(
                        data["error_message"] in response.get_data(as_text=True)
                    )
        self.assertTrue(user.verify_password("password"))

    def test_close_account_valid_input(self):
        """Test sending valid input to the close account view."""
        # create user
        role = Role.query.filter_by(name="Event Organizer").first()
        user = TestModelFactory.create_user(password="password")
        user.role = role
        db.session.add(user)
        db.session.commit()

        # Should be redirected if not logged in
        response = self.client.get("/settings/close_account", follow_redirects=True)
        self.assertTrue(response.status_code, 200)
        self.assertTrue(
            "Please log in to access this page" in response.get_data(as_text=True)
        )

        # log the user in
        with self.client:
            response = self.client.post(
                "/auth/login",
                data={"email": user.email, "password": "password"},
                follow_redirects=True,
            )

            # Send GET request
            response = self.client.get("/settings/close_account", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Account Information" in response.get_data(as_text=True))
            self.assertTrue("Change Password" in response.get_data(as_text=True))
            self.assertTrue("Change Email" in response.get_data(as_text=True))
            self.assertTrue("Close Your Account" in response.get_data(as_text=True))
            self.assertTrue(
                "Please enter &#34;CLOSE&#34; in the field below to confirm the closing of your account"
                in response.get_data(as_text=True)
            )

            # Send post request
            response = self.client.post(
                "/settings/close_account",
                data={"confirm": "CLOSE"},
                follow_redirects=True,
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(
                "Your account has been closed." in response.get_data(as_text=True)
            )
            # test for text in the navbar
            self.assertTrue("Stranger!" in response.get_data(as_text=True))
            self.assertTrue("Sign In" in response.get_data(as_text=True))
            self.assertTrue("Sign Up" in response.get_data(as_text=True))
            self.assertIsNone(
                User.query.get(1)
            )  # user should be deleted from the database

    def test_close_account_invalid_input(self):
        """Test sending invalid inputs to the close account view."""
        # create user
        role = Role.query.filter_by(name="Event Organizer").first()
        user = TestModelFactory.create_user(password="password")
        user.role = role
        db.session.add(user)
        db.session.commit()

        # log the user in
        with self.client:
            response = self.client.post(
                "/auth/login",
                data={"email": user.email, "password": "password"},
                follow_redirects=True,
            )

            for data in ViewFunctionTestData.INVALID_CLOSE_ACCOUNT_DATA:
                with self.subTest(data=data):
                    response = self.client.post(
                        "/settings/close_account",
                        data={"confirm": data["confirm"]},
                        follow_redirects=True,
                    )
                    self.assertTrue(
                        "Please enter &#34;CLOSE&#34;"
                        in response.get_data(as_text=True)
                    )


if __name__ == "__main__":
    unittest.main()
