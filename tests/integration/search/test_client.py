"""This module contains test cases for the class that wraps
the elasticsearch low level client."""


import unittest
from app import create_app
from tests.integration.testing_data import TestModelFactory
from app.models import Event
from app.search import FlaskSQLAlchemyMiddleware, ElasticsearchClient


class ElasticsearchClientTestCase(unittest.TestCase):
    """Class to run tests on the class that interfaces
    with the elasticsearch low level client.
    """

    def setUp(self):
        """Create application instance and insert necessary
        information into the database before each test.
        """
        self.app = create_app("testing", True)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.es_client = ElasticsearchClient(self.app.config["ELASTICSEARCH_URL"])

    def tearDown(self):
        """Pop application context, remove the db session,
        delete Elasticsearch testing index, and drop all
        tables in the database.
        """
        self.es_client.delete_index("testing_index")
        del self.es_client
        self.app_context.pop()

    def test_create_index_if_not_exists(self):
        """Test to confirm that indices are created automatically
        if they don't already exist.
        """
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event(
            title="Eric's Foobar", status="live", id=1
        )
        event.venue = venue
        document_body = FlaskSQLAlchemyMiddleware.extract_searchable_fields(event)
        self.es_client.add_to_index("testing_index", "testing", event.id, document_body)
        self.assertTrue(self.es_client._client.indices.exists("testing_index"))

    def test_delete_index(self):
        """Test that ensures that you can delete an index."""
        venue = TestModelFactory.create_venue()
        event = TestModelFactory.create_event(
            title="Eric's Foobar", status="live", id=1
        )
        event.venue = venue
        document_body = FlaskSQLAlchemyMiddleware.extract_searchable_fields(event)
        self.es_client.add_to_index("testing_index", "testing", event.id, document_body)
        self.assertTrue(self.es_client._client.indices.exists("testing_index"))

        self.es_client.delete_index("testing_index")
        self.assertFalse(self.es_client._client.indices.exists("testing_index"))



if __name__ == "__main__":
    unittest.main()
