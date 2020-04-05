import unittest
from integration.testing_data import ViewFunctionTestData, TestModelFactory
from app import create_app
from app.extensions import db
from app.models import User, Role


class AuthViewsTestCase(unittest.TestCase):
    """Class to test view functions in the auth blueprint."""

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

    def test_organizer_has_not_paid(self):
        """Test to ensure the before qpp request hook redirects
        an organizer who hasn't paid for their subscription
        can't access pages on the site until they pay.
        """
        role = Role.query.filter_by(name="Event Organizer").first()
        user = TestModelFactory.create_user(password="password", has_paid=False)
        user.role = role
        db.session.add(user)
        db.session.commit()

        with self.client:
            # send POST request to login view
            response = self.client.post(
                "/auth/login",
                data={"email": user.email, "password": "password"},
                follow_redirects=True,
            )

            # send GET request to home page. should issue a redirect
            response = self.client.get("/")
            self.assertEqual(response.status_code, 302)

            response = self.client.get("/", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(
                "Please complete your signup process by purchasing your subscription below."
                in response.get_data(as_text=True)
            )

    def test_login_valid_input(self):
        """Test the login view function for an event organizer."""

        # send GET request to login view
        response = self.client.get("/auth/login")
        self.assertEqual(response.status_code, 200)

        # some text that should be on the login screen
        self.assertTrue("Sign In" in response.get_data(as_text=True))
        self.assertTrue("Keep me logged in" in response.get_data(as_text=True))
        self.assertTrue("Forgot your password?" in response.get_data(as_text=True))
        self.assertTrue(
            'href="/auth/request_password_reset"' in response.get_data(as_text=True)
        )
        self.assertTrue("New user?" in response.get_data(as_text=True))
        self.assertTrue('href="/auth/register"' in response.get_data(as_text=True))

        # test for both organizers and sponsors logging in
        for login in ViewFunctionTestData.VALID_LOGINS:
            with self.subTest(login=login):
                # create user
                role = Role.query.filter_by(name=login["role_name"]).first()
                user = TestModelFactory.create_user(password="password", has_paid=False)
                user.role = role
                db.session.add(user)
                db.session.commit()

                # send POST request to login view
                response = self.client.post(
                    "/auth/login",
                    data={"email": login["email"], "password": login["password"]},
                    follow_redirects=True,
                )

                self.assertEqual(response.status_code, 200)
                self.assertTrue(login["message"] in response.get_data(as_text=True))

                # logged in users should see different things in the dropdown menu
                self.assertTrue("Account" in response.get_data(as_text=True))
                self.assertTrue("Settings" in response.get_data(as_text=True))
                self.assertTrue("Log Out" in response.get_data(as_text=True))
                if login["role_name"] == "Event Organizer":
                    self.assertTrue("Create Event" in response.get_data(as_text=True))
                    self.assertTrue(
                        "Organizer Profile" in response.get_data(as_text=True)
                    )
                    self.assertTrue("Manage Events" in response.get_data(as_text=True))
                else:
                    self.assertTrue(
                        "Sponsor Profile" in response.get_data(as_text=True)
                    )
                    self.assertTrue(
                        "Manage Sponsorships" in response.get_data(as_text=True)
                    )
                    self.assertTrue("Saved Events" in response.get_data(as_text=True))

                # need to delete user so as to no violate SQLAlchemy unique constraint
                db.session.delete(user)
                db.session.commit()

    def test_login_invalid_input(self):
        """Test for various invalid inputs for the login view."""

        # iterate through various tests of invalid parameters
        for login in ViewFunctionTestData.INVALID_LOGINS:
            with self.subTest(login=login):
                response = self.client.post(
                    "/auth/login",
                    data={"email": login["email"], "password": login["password"]},
                )
                self.assertTrue(
                    login["error_message"] in response.get_data(as_text=True)
                )

    def test_register_valid_input(self):
        """Test sending valid inputs to the register view function."""

        # GET request
        response = self.client.get("/auth/register")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Create an Account" in response.get_data(as_text=True))

        # test for both organizers and sponsors registering
        for registration in ViewFunctionTestData.VALID_REGISTRATIONS:
            with self.subTest(registration=registration):
                response = self.client.post(
                    "/auth/register",
                    data={
                        "first_name": registration["first_name"],
                        "last_name": registration["last_name"],
                        "company": registration["company"],
                        "email": registration["email"],
                        "password": registration["password"],
                        "confirm_password": registration["confirm_password"],
                        "role": registration["role"],
                    },
                    follow_redirects=True,
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(
                    registration["message"] in response.get_data(as_text=True)
                )

                # ensure the correct information is displaying in the top right-hand corner
                # of the navbar
                self.assertTrue("Sign In" in response.get_data(as_text=True))
                self.assertTrue("Sign Up" in response.get_data(as_text=True))
                self.assertFalse("Account" in response.get_data(as_text=True))
                self.assertFalse("Settings" in response.get_data(as_text=True))
                self.assertFalse("Log Out" in response.get_data(as_text=True))

    def test_register_invalid_input(self):
        """Test sending invalid inputs to the register view function."""

        # needed for two of the tests to check whether
        # there is a user with the given email or company already
        role = Role.query.filter_by(name="Event Organizer").first()
        user = TestModelFactory.create_user(
            password="password", company="Amazon", email="dave@amazon.com"
        )
        user.role = role
        db.session.add(user)
        db.session.commit()

        # iterate through invalid parameters
        for registration in ViewFunctionTestData.INVALID_REGISTRATIONS:
            with self.subTest(registration=registration):
                response = self.client.post(
                    "/auth/register",
                    data={
                        "first_name": registration["first_name"],
                        "last_name": registration["last_name"],
                        "company": registration["company"],
                        "email": registration["email"],
                        "password": registration["password"],
                        "confirm_password": registration["confirm_password"],
                        "role": registration["role"],
                    },
                    follow_redirects=True,
                )
                self.assertTrue(
                    registration["error_message"] in response.get_data(as_text=True)
                )

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

    def test_logout(self):
        """Test the logout view function."""

        # create user
        role = Role.query.filter_by(name="Event Organizer").first()
        user = TestModelFactory.create_user(password="password")
        user.role = role
        db.session.add(user)
        db.session.commit()

        # Should be redirected if not logged in
        response = self.client.get("/auth/logout", follow_redirects=True)
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

            # POST method shouldn't be allowed for this view
            response = self.client.post("/auth/logout", data={"fake": "Hello, World"})
            self.assertEqual(response.status_code, 405)
            self.assertTrue("Method Not Allowed" in response.get_data(as_text=True))

            # #GET request should successfully log the user out
            response = self.client.get("/auth/logout", follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Sign In" in response.get_data(as_text=True))
            self.assertTrue("Sign Up" in response.get_data(as_text=True))
            self.assertTrue(
                "You have been logged out." in response.get_data(as_text=True)
            )

    def test_organizer_permissions(self):
        """Test to ensure that event organizers can't  access
        the routes where they don't have the correct permissions
        """
        # create user
        role = Role.query.filter_by(name="Event Organizer").first()
        user = TestModelFactory.create_user(password="password")
        user.role = role
        db.session.add(user)
        db.session.commit()

        with self.client:
            # log the user in
            response = self.client.post(
                "/auth/login",
                data={"email": user.email, "password": "password"},
                follow_redirects=True,
            )

            for route in (
                ViewFunctionTestData.SPONSOR_ROUTES + ViewFunctionTestData.ADMIN_ROUTES
            ):
                with self.subTest(route=route):
                    response = self.client.get(route, follow_redirects=True)
                    self.assertEqual(response.status_code, 403)
                    self.assertTrue("Forbidden" in response.get_data(as_text=True))

    def test_sponsor_permissions(self):
        """Test to ensure that event sponsors can't  access
        the routes where they don't have the correct permissions
        """
        # create user
        role = Role.query.filter_by(name="Sponsor").first()
        user = TestModelFactory.create_user(password="password")
        user.role = role
        db.session.add(user)
        db.session.commit()

        with self.client:
            # log the user in
            response = self.client.post(
                "/auth/login",
                data={"email": user.email, "password": "password"},
                follow_redirects=True,
            )

            for route in (
                ViewFunctionTestData.ORGANIZER_ROUTES
                + ViewFunctionTestData.ADMIN_ROUTES
            ):
                with self.subTest(route=route):
                    response = self.client.get(route, follow_redirects=True)
                    self.assertEqual(response.status_code, 403)
                    self.assertTrue("Forbidden" in response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
