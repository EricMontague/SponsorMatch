"""This module contains a class that acts as a wrapper
around the low level Elasticsearch client.
"""

from elasticsearch import Elasticsearch
from app.search.response import SearchResponse



class ElasticsearchClient:
    """Class that is a wrapper around the low level
    elasticsearch client.
    """

    def __init__(self, hosts=None, transport_class=None, **kwargs):
        if transport_class:
            self._client = Elasticsearch(hosts, transport_class, **kwargs)
        else:
            self._client = Elasticsearch(hosts, **kwargs)
    
    def create_index(self, index):
        """Create a new index if it doesn't already exist."""
        if not self._client.indices.exists(index):
            self._client.indices.create(index)

    def query_index(self, index, query):
        """Query the given index and return the results of the search."""
        search_results = self._client.search(index=index, body=query.to_dict())
        return SearchResponse(search_results, query)

    def add_to_index(self, index, doc_type, document_id, body):
        """Add fields from the given model to the given index."""
        self._client.index(
            index=index, id=document_id, doc_type=doc_type, body=body
        )

    def remove_from_index(self, index, doc_type, document_id):
        """Remove a document in the given index based on the id
        of the given model
        """
        if self._client.exists(index=index, id=document_id, doc_type=doc_type):
            self._client.delete(index=index, id=document_id, doc_type=doc_type)

    def delete_index(self, index):
        """Delete the given index"""
        if self._client.indices.exists(index):
            self._client.indices.delete(index)



