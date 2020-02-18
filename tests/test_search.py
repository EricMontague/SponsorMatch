import unittest
import time
from app import create_app
from .testing_data import TestModelFactory
from app.search import add_to_index, remove_from_index, query_index, delete_index
from app.models import Event
from elasticsearch2.exceptions import NotFoundError, RequestError, \
    SerializationError


class SearchTestCase(unittest.TestCase):
    """Class to run tests on the functions that interface
    with the elasticsearch api.
    """

    def setUp(self):
        """Create application instance and insert necessary
        information into the database before each test.
        """
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Pop application context, remove the db session,
        delete Elasticsearch testing index, and drop all 
        tables in the database.
        """
        if self.app.elasticsearch.indices.exists("testing_index"):
            self.app.elasticsearch.indices.delete("testing_index")
        self.app_context.pop()

    def test_create_index_if_not_exists(self):
        """Test to confirm that indices are created automatically
        if they don't already exist.
        """
        event = TestModelFactory.create_event(title="Eric's Foobar", status="live", id=1)
        add_to_index("testing_index", "testing", event)
        self.assertTrue(self.app.elasticsearch.indices.exists("testing_index"))

    def test_delete_index(self):
        """Test that ensures that you can delete an index."""
        event = TestModelFactory.create_event(title="Foobar", status="live", id=1)
        add_to_index("testing_index", "testing", event)
        self.assertTrue(self.app.elasticsearch.indices.exists("testing_index"))
        delete_index("testing_index")
        self.assertFalse(self.app.elasticsearch.indices.exists("testing_index"))

    def test_add_to_index(self):
        """Test that ensures that an event can be added
        to an index in Elasticsearch.
        """
        event = TestModelFactory.create_event(title="Foobar", status="live", id=1)
     
        add_to_index("testing_index", "testing", event)

        #delay needed otherwise the GET request to Elasticsearch API
        #will get there before the resource is ready to be retrieved
        time.sleep(2)
        ids, num_results = query_index("testing_index", "Foobar", 1, 1)
        self.assertEqual(ids[0], event.id)
        self.assertEqual(num_results, 1)

    def test_remove_from_index(self):
        """Test that ensures that an event can be deleted
        from Elasticsearch.
        """
        event = TestModelFactory.create_event(title="Foobar", status="live", id=1)
        
        add_to_index("testing_index", "testing", event)
        time.sleep(2)
        ids, num_results = query_index("testing_index", "Foobar", 1, 1)
        self.assertEqual(ids[0], event.id)
        self.assertEqual(num_results, 1)

        remove_from_index("testing_index", "testing", event)
        time.sleep(2)
        ids, num_results = query_index("testing_index", "Foobar", 1, 1)
        self.assertEqual(ids, [])
        self.assertEqual(num_results, 0)
        
    def test_query_index_exact_matches(self):
        """Test that ensures that Elasticsearch
        returns accurate query results when the exact phrase
        is searched for.
        """
        #instantiate objects
        event_one = TestModelFactory.create_event(title="Foobar", status="live", id=1)
        event_two = TestModelFactory.create_event(title="Eric's Party", status="live", id=2)
       
        #add both to the index
        add_to_index("testing_index", "testing", event_one)
        add_to_index("testing_index", "testing", event_two)

        time.sleep(2)
        #run queries and check for expected and unexpected results
        ids, num_results = query_index("testing_index", "Foobar", 1, 2)
        self.assertEqual(ids[0], event_one.id)
        self.assertNotEqual(ids[0], event_two.id)
        self.assertEqual(num_results, 1)

        ids, num_results = query_index("testing_index", "Eric's Party", 1, 2)
        self.assertEqual(ids[0], event_two.id)
        self.assertNotEqual(ids[0], event_one.id)
        self.assertEqual(num_results, 1)

        #search should be case insensitive
        ids, num_results = query_index("testing_index", "eric's party", 1, 2)
        self.assertEqual(ids[0], event_two.id)
        self.assertNotEqual(ids[0], event_one.id)
        self.assertEqual(num_results, 1)

    def test_query_index_no_search_results(self):
        """Test that elasticsearch provides no search results
        when an incorrect query is sent.
        """
        #instantiate objects
        event_one = TestModelFactory.create_event(title="Foobar", status="live", id=1)
        event_two = TestModelFactory.create_event(title="Eric's Party", status="live", id=2)

        #add both to the index
        add_to_index("testing_index", "testing", event_one)
        add_to_index("testing_index", "testing", event_two)

        time.sleep(2)
        #search should return nothing
        ids, num_results = query_index("testing_index", "Philly", 1, 2)
        self.assertEqual(ids, [])
        self.assertEqual(num_results, 0)

        #description is not a searchable attribute
        ids, num_results = query_index("testing_index", "This is the best event", 1, 2)
        self.assertEqual(ids, [])
        self.assertEqual(num_results, 0)

    def test_query_index_partial_matches(self):
        """Test that Elasticsearch still provides search results
        on partial matches of queries.
        """
        #instantiate objects
        event_one = TestModelFactory.create_event(title="Eric's Foobar", status="live", id=1)
        event_two = TestModelFactory.create_event(title="Eric's Party", status="live", id=2)
        #add both to the index
        add_to_index("testing_index", "testing", event_one)
        add_to_index("testing_index", "testing", event_two)
        
        time.sleep(2)

        ids, num_results = query_index("testing_index", "Foo", 1, 2)
        self.assertEqual(ids, [])
        self.assertEqual(num_results, 0)

        ids, num_results = query_index("testing_index", "Part", 1, 2)
        self.assertEqual(ids, [])
        self.assertEqual(num_results, 0)

        ids, num_results = query_index("testing_index", "Fooba", 1, 2)
        self.assertEqual(ids, [])
        self.assertEqual(num_results, 0)

        ids, num_results = query_index("testing_index", "Eric's Fooba", 1, 2)
        self.assertEqual(ids[0], event_two.id)
        self.assertEqual(ids[1], event_one.id)
        self.assertEqual(num_results, 2)

        ids, num_results = query_index("testing_index", "Eric", 1, 2)
        self.assertEqual(ids, [])
        self.assertEqual(num_results, 0)

        ids, num_results = query_index("testing_index", "Party", 1, 2)
        self.assertEqual(ids[0], event_two.id)
        self.assertNotEqual(ids[0], event_one.id)
        self.assertEqual(num_results, 1)

        ids, num_results = query_index("testing_index", "Eric Party", 1, 2)
        self.assertEqual(ids[0], event_two.id)
        self.assertNotEqual(ids[0], event_one.id)
        self.assertEqual(num_results, 1)

    def test_query_index_invalid_parameters(self):
        """Test that invalid parameters to the function
        throw the approriate exceptions.
        """
        #instantiate objects
        event = TestModelFactory.create_event(title="Foobar", status="live", id=1)
        add_to_index("testing_index", "testing", event)

        time.sleep(2)

        #searching sugin a list
        with self.assertRaises(RequestError):
            ids, num_results = query_index("testing_index", ["Eric's", "Foobar"], 1, 1)

        #searching using a model
        with self.assertRaises(SerializationError):
            ids, num_results = query_index("testing_index", event, 1, 1)

        #zero as a starting page number
        with self.assertRaises(RequestError):
            ids, num_results = query_index("testing_index", "Eric's Foobar", 0, 1)

        #negative results per page
        with self.assertRaises(RequestError):
            ids, num_results = query_index("testing_index", "Eric's Foobar", 1, -1)

        #string page number
        with self.assertRaises(TypeError):
            ids, num_results = query_index("testing_index", "Eric's Foobar", "1", 1)

        #string results per page
        with self.assertRaises(RequestError):
            ids, num_results = query_index("testing_index", "Eric's Foobar", 1, "1")


        #searching with an index that doesn't exist
        with self.assertRaises(NotFoundError):
            ids, num_results = query_index("Sponsorship", "Eric's Foobar", 1, 1)
        

if __name__ == '__main__':
    unittest.main()
