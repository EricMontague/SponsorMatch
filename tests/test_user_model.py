import unittest
import time
from datetime import datetime
from app import create_app, db
from .testing_data import TestModelFactory
from app.models import Permission, User, AnonymousUser


class UserModelTestCase(unittest.TestCase):
    """Class to run tests on the User model"""

    def setUp(self):
        """Manually push application context and setup the database."""
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Remove database session, drop all tables, 
        and pop the application context.
        """
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        """Test that the password hash can be successfully set"""
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        db.session.add(user)
        db.session.commit()
        self.assertIsNotNone(user.password_hash)

    def test_no_password_getter(self):
        """Test that the password attribute is not readable"""
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        db.session.add(user)
        db.session.commit()
        with self.assertRaises(AttributeError):
            user.password

    def test_password_verification(self):
        """Test user password verification"""
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        db.session.add(user)
        db.session.commit()
        self.assertTrue(user.verify_password("password"))
        self.assertFalse(user.verify_password("pass"))

    def test_password_salts_are_random(self):
        """Test that different passwords generate different
        password hashes
        """
        role = TestModelFactory.create_role("Event Organizer")
        user_one = TestModelFactory.create_user(password="password_one", company="ABC Corp", email="greg@gmail.com")
        user_two = TestModelFactory.create_user(password="password_two", company="DEF Corp", email="brad@gmail.com")
        user_one.role = role
        user_two.role = role
        db.session.add_all([user_one, user_two])
        db.session.commit()
        self.assertNotEqual(user_one.password_hash, user_two.password_hash)

    def test_valid_password_reset_token(self):
        """Test to confirm that the password reset process works
        when a valid token is provided.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user(password="password")
        user.role = role
        db.session.add(user)
        db.session.commit()
        token = user.generate_password_reset_token()
        new_password = "dog"
        self.assertTrue(User.reset_password(token, new_password))
        self.assertTrue(user.verify_password(new_password))
        self.assertFalse(user.verify_password("password"))

    def test_invalid_password_reset_token(self):
        """Test to confirm that an invalid token can't be used to
        reset a user's password
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user(password="password")
        user.role = role
        db.session.add(user)
        db.session.commit()
        token = user.generate_password_reset_token()
        new_password = "dog"
        self.assertFalse(User.reset_password(token + "foobar", new_password))
        self.assertTrue(user.verify_password("password"))

    def test_expired_password_reset_token(self):
        """Test to confirm that a user can't reset their password with
        an expired token
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user(password="password")
        user.role = role
        db.session.add(user)
        db.session.commit()
        token = user.generate_password_reset_token(expiration=2)
        new_password = "dog"
        time.sleep(3)
        self.assertFalse(User.reset_password(token, new_password))
        self.assertTrue(user.verify_password("password"))

    def test_valid_change_email_token(self):
        """Test to confirm that the change email process works
        when provided a valid token.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user(email="greg@gmail.com")
        user.role = role
        db.session.add(user)
        db.session.commit()
        new_email = "john@gmail.com"
        token = user.generate_change_email_token(new_email)
        self.assertTrue(user.change_email(token))
        self.assertEqual(user.email, new_email)
        self.assertNotEqual(user.email, "greg@gmail.com")

    def test_invalid_change_email_token(self):
        """Test to ensure that a user cannot change their email
        with an invalid token
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user(email="dave@gmail.com")
        user.role = role
        db.session.add(user)
        db.session.commit()
        new_email = "john@gmail.com"
        token = user.generate_change_email_token(new_email)
        self.assertFalse(user.change_email(token + "foobar"))
        self.assertEqual(user.email, "dave@gmail.com")

    def test_expired_change_email_token(self):
        """Test to ensure that a user can't change their email with an
        expired token
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user(email="dave@gmail.com")
        user.role = role
        db.session.add(user)
        db.session.commit()
        new_email = "john@gmail.com"
        token = user.generate_change_email_token(new_email, expiration=2)
        time.sleep(3)
        self.assertFalse(user.change_email(token))
        self.assertEqual(user.email, "dave@gmail.com")

    def test_duplicate_change_email_token(self):
        """Test to ensure that a user can't change their email to the email
        of another user. Only one user can have a particular email address.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user_one = TestModelFactory.create_user(password="password_one", email="dave@gmail.com", company="ABC Corp")
        user_two = TestModelFactory.create_user(password="password_two", email="joe@gmail.com", company="DEF Corp")
        user_one.role = role
        user_two.role = role
        db.session.add_all([user_one, user_two])
        db.session.commit()
        new_email = user_two.email
        token = user_one.generate_change_email_token(new_email)
        self.assertFalse(user_one.change_email(token))
        self.assertEqual(user_one.email, "dave@gmail.com")

    def test_is_organizer(self):
        """Test to ensure that a user is the event organizer."""
        role = TestModelFactory.create_role("Event Organizer")
        user_one = TestModelFactory.create_user(password="password_one", email="dave@gmail.com", company="ABC Corp")
        user_two = TestModelFactory.create_user(password="password_two", email="joe@gmail.com", company="DEF Corp")
        user_one.role = role
        user_two.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "live")
        event.user = user_one
        event.venue = venue
        db.session.add_all([user_one, user_two, event])
        db.session.commit()
        self.assertTrue(user_one.is_organizer(event))
        self.assertFalse(user_two.is_organizer(event))

    def test_organizer_permissions(self):
        """Test the permission of a user with
        the permissions to create an event."""
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        db.session.add(user)
        db.session.commit()

        self.assertFalse(user.can(Permission.SPONSOR_EVENT))
        self.assertFalse(user.can(Permission.ADMIN))
        self.assertTrue(user.can(Permission.CREATE_EVENT))
        
    def test_sponsor_permissions(self):
        """Test the permissions of a user with the 
        permissions to sponsor an event.
        """
        role = TestModelFactory.create_role("Sponsor")
        user = TestModelFactory.create_user()
        user.role = role
        db.session.add(user)
        db.session.commit()

        self.assertFalse(user.can(Permission.ADMIN))
        self.assertTrue(user.can(Permission.SPONSOR_EVENT))
        self.assertFalse(user.can(Permission.CREATE_EVENT))
        
    def test_admin_permissions(self):
        """Test the permissions of a user with administrator permissions."""
        role = TestModelFactory.create_role("Administrator")
        user = TestModelFactory.create_user()
        user.role = role
        db.session.add(user)
        db.session.commit()

        self.assertTrue(user.is_administrator())
        self.assertTrue(user.can(Permission.ADMIN))
        self.assertTrue(user.can(Permission.SPONSOR_EVENT))
        self.assertTrue(user.can(Permission.CREATE_EVENT))

    def test_anonymous_user(self):
        """Test the permissions of an anonymous user."""
        user = AnonymousUser()
        self.assertFalse(user.can(Permission.ADMIN))
        self.assertFalse(user.can(Permission.SPONSOR_EVENT))
        self.assertFalse(user.can(Permission.CREATE_EVENT))

    def test_member_since(self):
        """Test the default timestamp option for the member since
        attribute is properly set.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user()
        user.role = role
        db.session.add(user)
        db.session.commit()

        self.assertTrue(
            (datetime.utcnow() - user.member_since).total_seconds() < 3)

    def test_save_event(self):
        """Test that a user can save an event."""
        role = TestModelFactory.create_role("Sponsor")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "live")
        event.user = user
        event.venue = venue
        db.session.add_all([user, event])
        db.session.commit()

        user.save(event)
        db.session.commit()
        self.assertTrue(user.has_saved(event))

    def test_unsave_event(self):
        """Test that the user can remove an event from
        their list of saved events.
        """
        role = TestModelFactory.create_role("Sponsor")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "live")
        event.user = user
        event.venue = venue
        user.save(event)
        db.session.add_all([user, event])
        db.session.commit()

        user.unsave(event)
        db.session.commit()
        self.assertFalse(user.has_saved(event))

    def test_num_live_events_hosted(self):
        """Test the number of live events hosted by a user."""
        role = TestModelFactory.create_role("Sponsor")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "live")
        event.user = user
        event.venue = venue
        user.save(event)
        db.session.add_all([user, event])
        db.session.commit()

        live_events = user.num_events_hosted("live")
        past_events = user.num_events_hosted("past")
        all_events = user.num_events_hosted()
        self.assertEqual(live_events, 1)
        self.assertEqual(past_events, 0)
        self.assertEqual(all_events, 1)

    def test_num_past_events_hosted(self):
        """Test the number of past events hosted by a user."""
        role = TestModelFactory.create_role("Sponsor")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "past")
        event.user = user
        event.venue = venue
        user.save(event)
        db.session.add_all([user, event])
        db.session.commit()

        live_events = user.num_events_hosted("live")
        past_events = user.num_events_hosted("past")
        all_events = user.num_events_hosted()
        self.assertEqual(live_events, 0)
        self.assertEqual(past_events, 1)
        self.assertEqual(all_events, 1)

    def test_num_events_hosted_excluding_draft_events(self):
        """Test the number of events hosted by a user.
        If the event is in draft status, it should not be
        included in the calculation.
        """
        role = TestModelFactory.create_role("Sponsor")
        user = TestModelFactory.create_user()
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Test Event", "draft")
        event.user = user
        event.venue = venue
        user.save(event)
        db.session.add_all([user, event])
        db.session.commit()

        live_events = user.num_events_hosted("live")
        past_events = user.num_events_hosted("past")
        all_events = user.num_events_hosted()
        self.assertEqual(live_events, 0)
        self.assertEqual(past_events, 0)
        self.assertEqual(all_events, 0)

    def test_num_current_events_sponsored(self):
        """Test the number of events sponsored by a 
        user that are ongoing.
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

        current_events = user.num_events_sponsored("current")
        past_events = user.num_events_sponsored("past")
        all_events = user.num_events_sponsored()
        self.assertEqual(current_events, 1)
        self.assertEqual(past_events, 0)
        self.assertEqual(all_events, 1)

    def test_num_past_events_sponsored(self):
        """Test the number of events sponsored by a 
        user that have ended.
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

        current_events = user.num_events_sponsored("current")
        past_events = user.num_events_sponsored("past")
        all_events = user.num_events_sponsored()
        self.assertEqual(current_events, 0)
        self.assertEqual(past_events, 1)
        self.assertEqual(all_events, 1)


    def test_num_events_sponsored_excluding_pending_sponsorships(self):
        """Test the number of events sponsored by a user.
        If a sponsorship doesn't have a timestamp or confirmation code,
        it is marked as pending and shouldn't be counted towards
        the number of sponsored events.
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

        current_events = user.num_events_sponsored("current")
        past_events = user.num_events_sponsored("past")
        all_events = user.num_events_sponsored()
        self.assertEqual(current_events, 0)
        self.assertEqual(past_events, 0)
        self.assertEqual(all_events, 0)

    def test_has_purchased_package_sponsorship_completed(self):
        """Test to confirm whether a user has purchased a package already.
        A sponsor ship is complete if it has a timestamp and confirmation code.
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

        self.assertTrue(user.has_purchased(package))

    def test_has_purchased_package_sponsorship_pending(self):
        """Test to confirm whether a user has purchased a package already.
        This shoul return False if the sponsorship deal is pending.
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

        self.assertFalse(user.has_purchased(package))

    def test_profile_photo_getter(self):
        """Test that functionality of the profile_photo method."""

        path = "/Users/ericmontague/sponsormatch/app/static/images/test_image.jpg"
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user(profile_photo_path=path)
        user.role = role
        db.session.add(user)
        db.session.commit()

        profile_photo_path = user.profile_photo()
        self.assertEqual(profile_photo_path, "images/test_image.jpg")


if __name__ == '__main__':
    unittest.main()
    