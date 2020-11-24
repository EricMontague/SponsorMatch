"""This module contains test cases to test the functionality
between SQLAlchemy and Elasticsearch.
"""


import unittest
import time
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from tests.integration.testing_data import TestModelFactory
from app.models import Event
from app.search import MatchQuery
from elasticsearch.exceptions import NotFoundError, RequestError, SerializationError


class SearhcMiddlewareTestCase(unittest.TestCase):
    """Class to run tests ensuring the communication between
    the event model and Elasticsearh.
    """

    def setUp(self):
        """Create application instance and insert necessary
        information into the database before each test.
        """
        self.app = create_app("testing", True)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.search_middleware = self.app.sqlalchemy_search_middleware
        db.create_all()
        Event.__tablename__ = "testing_index"
        Event.__doctype__ = "testing"

    def tearDown(self):
        """Pop application context, remove the db session,
        delete Elasticsearch testing index, and drop all tables in the database.
        """
        self.search_middleware._elasticsearch_client.delete_index("testing_index")
        db.session.remove()
        db.drop_all()
        del self.search_middleware
        self.app_context.pop()

    def test_search_exact_matches(self):
        """Test that the search method returns
        accurate search results for exact matches.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user(
            password="password_one", email="dave@gmail.com", company="ABC Corp"
        )
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Eric's Party", "live", id=1)
        event.venue = venue
        event.user = user
        db.session.add_all([user, event])
        db.session.commit()

        # need to wait 2 seconds before sending the GET request to the Elasticsearch API
        # or else the resource won't be there
        time.sleep(2)
        match_query1 = MatchQuery("title", "Eric's Party")
        response, pagination = self.search_middleware.search(Event, match_query1)
        self.assertEqual(pagination.items.first(), event)
        self.assertEqual(response.total, 1)

        # lowercase should work too
        match_query2 = MatchQuery("title", "Eeric's Party")
        response, pagination = self.search_middleware.search(Event, match_query2)
        self.assertEqual(pagination.items.first(), event)
        self.assertEqual(response.total, 1)

    def test_no_search_results(self):
        """Test that the search method returns no 
        search results when the event title
        doesn't exist in Elasticsearch.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user(
            password="password_one", email="dave@gmail.com", company="ABC Corp"
        )
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Eric's Party", "live", id=1)
        event.user = user
        event.venue = venue
        db.session.add_all([user, event])
        db.session.commit()

        time.sleep(2)

        # search should return nothing
        match_query1 = MatchQuery("title", "Philly")
        response, pagination = self.search_middleware.search(Event, match_query1)
        self.assertIsNone(pagination.items.first())
        self.assertEqual(response.total, 0)

    def test_search_partial_matches(self):
        """Test that the search method returns the
        appropriate reulsts for partial matches.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user(
            password="password_one", email="dave@gmail.com", company="ABC Corp"
        )
        user.role = role
        venue_one = TestModelFactory.create_venue(address="123 Main St.")
        venue_two = TestModelFactory.create_venue(address="456 Main St.")
        event_one = TestModelFactory.create_event("Eric's Foobar", "live", id=1)
        event_two = TestModelFactory.create_event(
            "Eric's Party", "live", event_type="Convention", event_category="Sports", id=2
        )
        event_one.user = user
        event_two.user = user
        event_one.venue = venue_one
        event_two.venue = venue_two
        db.session.add_all([user, event_one, event_two])
        db.session.commit()

        time.sleep(2)

        match_query1 = MatchQuery("title", "Foo")
        response, pagination = self.search_middleware.search(Event, match_query1)
        self.assertIsNone(pagination.items.first())
        self.assertEqual(response.total, 0)

        match_query2 = MatchQuery("title", "Part")
        response, pagination = self.search_middleware.search(Event, match_query2)
        self.assertIsNone(pagination.items.first())
        self.assertEqual(response.total, 0)

        match_query3 = MatchQuery("title", "Eric's Fooba")
        response, pagination = self.search_middleware.search(Event, match_query3)
        self.assertEqual(pagination.items.all(), [event_one, event_two])
        self.assertEqual(response.total, 2)

        match_query4 = MatchQuery("title", "Party")
        response, pagination = self.search_middleware.search(Event, match_query4)
        self.assertEqual(pagination.items.first(), event_two)
        self.assertNotEqual(pagination.items.first(), event_one)
        self.assertEqual(response.total, 1)

    def test_event_search_invalid_parameters(self):
        """Test that invalid parameters to the search method
        throw the approriate exceptions.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user(
            password="password_one", email="dave@gmail.com", company="ABC Corp"
        )
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Eric's Foobar", "live", id=1)
        event.user = user
        event.venue = venue
        db.session.add_all([user, event])
        db.session.commit()

        time.sleep(2)

        # searching using a list
        with self.assertRaises(RequestError):
            match_query = MatchQuery("title", ["Eric's", "Foobar"])
            response, pagination = self.search_middleware.search(Event, match_query)

        # searching using a model
        with self.assertRaises(SerializationError):
            match_query = MatchQuery("title", event)
            response, pagination = self.search_middleware.search(Event, match_query)

    def test_add_after_commit(self):
        """Test to confirm that events added to the database
        are reflected in Elasticsearch after each commit.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user(
            password="password_one", email="dave@gmail.com", company="ABC Corp"
        )
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Foobar", "live", id=1)
        event.user = user
        event.venue = venue
        db.session.add_all([user, event])
        db.session.commit()

        time.sleep(2)

        match_query = MatchQuery("title", "Foobar")
        response, pagination = self.search_middleware.search(Event, match_query)
        self.assertEqual(pagination.items.first(), event)
        self.assertEqual(response.total, 1)

    def test_delete_after_commit(self):
        """Test to confirm that events deleted from the database.
        are reflected in Elasticsearch after each commit.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user(
            password="password_one", email="dave@gmail.com", company="ABC Corp"
        )
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Foobar", "live", id=1)
        event.user = user
        event.venue = venue
        db.session.add_all([user, event])
        db.session.commit()

        time.sleep(2)

        match_query1 = MatchQuery("title", "Foobar")
        response, pagination = self.search_middleware.search(Event, match_query1)
        self.assertEqual(pagination.items.first(), event)
        self.assertEqual(response.total, 1)

        db.session.delete(event)
        db.session.commit()

        time.sleep(2)

        match_query2 = MatchQuery("title", "Foobar")
        response, pagination = self.search_middleware.search(Event, match_query2)
        self.assertIsNone(pagination.items.first())
        self.assertEqual(response.total, 0)

    def test_update_after_commit(self):
        """Test to confirm that events updated in the database
        are reflected in Elasticsearch after each commit.
        """
        role = TestModelFactory.create_role("Event Organizer")
        user = TestModelFactory.create_user(
            password="password_one", email="dave@gmail.com", company="ABC Corp"
        )
        user.role = role
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event("Foobar", "live", id=1)
        event.user = user
        event.venue = venue
        db.session.add_all([user, event])
        db.session.commit()

        time.sleep(2)
        # confirm that the event is in Elasticsearch
        match_query1 = MatchQuery("title", "Foobar")
        response, pagination = self.search_middleware.search(Event, match_query1)
        self.assertEqual(pagination.items.first(), event)
        self.assertEqual(response.total, 1)

        # update title
        event.title = "Eric's Party"
        db.session.commit()

        time.sleep(2)

        # check that the update was recognized
        match_query2 = MatchQuery("title", "Eric's Party")
        response, pagination = self.search_middleware.search(Event, match_query2)
        self.assertEqual(pagination.items.first(), event)
        self.assertEqual(response.total, 1)



if __name__ == "__main__":
    unittest.main()
