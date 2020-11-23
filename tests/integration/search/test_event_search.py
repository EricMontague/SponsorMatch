# """This module contains test cases to test the functionality
# between SQLAlchemy and Elasticsearch.
# """


# import unittest
# import time
# from datetime import datetime, timedelta
# from app import create_app
# from app.extensions import db
# from tests.integration.testing_data import TestModelFactory
# from app.models import Event
# from elasticsearch.exceptions import NotFoundError, RequestError, SerializationError


# class EventSearchTestCase(unittest.TestCase):
#     """Class to run tests ensuring the communication between
#     the event model and Elasticsearh.
#     """

#     def setUp(self):
#         """Create application instance and insert necessary
#         information into the database before each test.
#         """
#         self.app = create_app("testing", True)
#         self.app_context = self.app.app_context()
#         self.app_context.push()
#         db.create_all()
#         Event.__tablename__ = "testing_index"
#         Event.__doctype__ = "testing"

#     def tearDown(self):
#         """Pop application context, remove the db session,
#         delete Elasticsearch testing index, and drop all tables in the database.
#         """
#         Event.delete_index("testing_index")
#         db.session.remove()
#         db.drop_all()
#         self.app_context.pop()

#     def test_search_exact_matches(self):
#         """Test that the search method returns
#         accurate search results for exact matches.
#         """
#         role = TestModelFactory.create_role("Event Organizer")
#         user = TestModelFactory.create_user(
#             password="password_one", email="dave@gmail.com", company="ABC Corp"
#         )
#         user.role = role
#         venue = TestModelFactory.create_venue()
#         event = TestModelFactory.create_event("Eric's Party", "live")
#         event.venue = venue
#         event.user = user
#         db.session.add_all([user, event])
#         db.session.commit()

#         # need to wait 2 seconds before sending the GET request to the Elasticsearch API
#         # or else the resource won't be there
#         time.sleep(2)

#         query_obj, num_results = Event.search("Eric's Party", 1, 1)
#         self.assertEqual(query_obj.first(), event)
#         self.assertEqual(num_results, 1)

#         # lowercase should work too
#         query_obj, num_results = Event.search("eric's party", 1, 1)
#         self.assertEqual(query_obj.first(), event)
#         self.assertEqual(num_results, 1)

#     def test_no_search_results(self):
#         """Test that the search method returns no 
#         search results when the event title
#         doesn't exist in Elasticsearch.
#         """
#         role = TestModelFactory.create_role("Event Organizer")
#         user = TestModelFactory.create_user(
#             password="password_one", email="dave@gmail.com", company="ABC Corp"
#         )
#         user.role = role
#         venue = TestModelFactory.create_venue()
#         event = TestModelFactory.create_event("Eric's Party", "live")
#         event.user = user
#         event.venue = venue
#         db.session.add_all([user, event])
#         db.session.commit()

#         time.sleep(2)

#         # search should return nothing
#         query_obj, num_results = Event.search("Philly", 1, 1)
#         self.assertIsNone(query_obj.first())
#         self.assertEqual(num_results, 0)

#         # description is not a searchable attribute
#         query_obj, num_results = Event.search(event.description, 1, 1)
#         self.assertIsNone(query_obj.first())
#         self.assertEqual(num_results, 0)

#     def test_search_partial_matches(self):
#         """Test that the search method returns the
#         appropriate reulsts for partial matches.
#         """
#         role = TestModelFactory.create_role("Event Organizer")
#         user = TestModelFactory.create_user(
#             password="password_one", email="dave@gmail.com", company="ABC Corp"
#         )
#         user.role = role
#         venue_one = TestModelFactory.create_venue(address="123 Main St.")
#         venue_two = TestModelFactory.create_venue(address="456 Main St.")
#         event_one = TestModelFactory.create_event("Eric's Foobar", "live")
#         event_two = TestModelFactory.create_event(
#             "Eric's Party", "live", event_type="Convention", event_category="Sports"
#         )
#         event_one.user = user
#         event_two.user = user
#         event_one.venue = venue_one
#         event_two.venue = venue_two
#         db.session.add_all([user, event_one, event_two])
#         db.session.commit()

#         time.sleep(2)

#         query_obj, num_results = Event.search("Foo", 1, 2)
#         self.assertIsNone(query_obj.first())
#         self.assertEqual(num_results, 0)

#         query_obj, num_results = Event.search("Part", 1, 2)
#         self.assertIsNone(query_obj.first())
#         self.assertEqual(num_results, 0)

#         query_obj, num_results = Event.search("Fooba", 1, 2)
#         self.assertIsNone(query_obj.first())
#         self.assertEqual(num_results, 0)

#         query_obj, num_results = Event.search("Eric's Fooba", 1, 2)
#         self.assertEqual(query_obj.all()[0], event_one)
#         self.assertEqual(query_obj.all()[1], event_two)
#         self.assertEqual(num_results, 2)

#         query_obj, num_results = Event.search("Eric", 1, 2)
#         self.assertIsNone(query_obj.first())
#         self.assertEqual(num_results, 0)

#         query_obj, num_results = Event.search("Party", 1, 2)
#         self.assertEqual(query_obj.all()[0], event_two)
#         self.assertNotEqual(query_obj.all()[0], event_one)
#         self.assertEqual(num_results, 1)

#         query_obj, num_results = Event.search("Eric Party", 1, 2)
#         self.assertEqual(query_obj.all()[0], event_two)
#         self.assertNotEqual(query_obj.all()[0], event_one)
#         self.assertEqual(num_results, 1)

#     def test_event_search_invalid_parameters(self):
#         """Test that invalid parameters to the search method
#         throw the approriate exceptions.
#         """
#         role = TestModelFactory.create_role("Event Organizer")
#         user = TestModelFactory.create_user(
#             password="password_one", email="dave@gmail.com", company="ABC Corp"
#         )
#         user.role = role
#         venue = TestModelFactory.create_venue()
#         event = TestModelFactory.create_event("Eric's Foobar", "live")
#         event.user = user
#         event.venue = venue
#         db.session.add_all([user, event])
#         db.session.commit()

#         time.sleep(2)

#         # searching using a list
#         with self.assertRaises(RequestError):
#             query_obj, num_results = Event.search(["Eric's", "Foobar"], 1, 1)

#         # searching using a model
#         with self.assertRaises(SerializationError):
#             query_obj, num_results = Event.search(event, 1, 1)

#         # string page number
#         with self.assertRaises(TypeError):
#             query_obj, num_results = Event.search("Eric's Foobar", "1", 1)

#         # string results per page
#         with self.assertRaises(RequestError):
#             query_obj, num_results = Event.search("Eric's Foobar", 1, "1")

#     def test_add_after_commit(self):
#         """Test to confirm that events added to the database
#         are reflected in Elasticsearch after each commit.
#         """
#         role = TestModelFactory.create_role("Event Organizer")
#         user = TestModelFactory.create_user(
#             password="password_one", email="dave@gmail.com", company="ABC Corp"
#         )
#         user.role = role
#         venue = TestModelFactory.create_venue()
#         event = TestModelFactory.create_event("Foobar", "live")
#         event.user = user
#         event.venue = venue
#         db.session.add_all([user, event])
#         db.session.commit()

#         time.sleep(2)

#         query_obj, num_results = Event.search("Foobar", 1, 1)
#         self.assertEqual(query_obj.first(), event)
#         self.assertEqual(num_results, 1)

#     def test_delete_after_commit(self):
#         """Test to confirm that events deleted from the database.
#         are reflected in Elasticsearch after each commit.
#         """
#         role = TestModelFactory.create_role("Event Organizer")
#         user = TestModelFactory.create_user(
#             password="password_one", email="dave@gmail.com", company="ABC Corp"
#         )
#         user.role = role
#         venue = TestModelFactory.create_venue()
#         event = TestModelFactory.create_event("Foobar", "live")
#         event.user = user
#         event.venue = venue
#         db.session.add_all([user, event])
#         db.session.commit()

#         time.sleep(2)

#         query_obj, num_results = Event.search("Foobar", 1, 1)
#         self.assertEqual(query_obj.first(), event)
#         self.assertEqual(num_results, 1)

#         db.session.delete(event)
#         db.session.commit()

#         time.sleep(2)

#         query_obj, num_results = Event.search("Foobar", 1, 1)
#         self.assertIsNone(query_obj.first())
#         self.assertEqual(num_results, 0)

#     def test_update_after_commit(self):
#         """Test to confirm that events updated in the database
#         are reflected in Elasticsearch after each commit.
#         """
#         role = TestModelFactory.create_role("Event Organizer")
#         user = TestModelFactory.create_user(
#             password="password_one", email="dave@gmail.com", company="ABC Corp"
#         )
#         user.role = role
#         venue = TestModelFactory.create_venue()
#         event = TestModelFactory.create_event("Foobar", "live")
#         event.user = user
#         event.venue = venue
#         db.session.add_all([user, event])
#         db.session.commit()

#         time.sleep(2)

#         # confirm that the event is in Elasticsearch
#         query_obj, num_results = Event.search("Foobar", 1, 1)
#         self.assertEqual(query_obj.first(), event)
#         self.assertEqual(num_results, 1)

#         # update title
#         event.title = "Eric's Party"
#         db.session.commit()

#         time.sleep(2)

#         # check that the update wa recognized
#         query_obj, num_results = Event.search("Eric's Party", 1, 1)
#         self.assertEqual(query_obj.first(), event)
#         self.assertEqual(num_results, 1)

#         query_obj, num_results = Event.search("Foobar", 1, 1)
#         self.assertIsNone(query_obj.first())
#         self.assertEqual(num_results, 0)


# if __name__ == "__main__":
#     unittest.main()
