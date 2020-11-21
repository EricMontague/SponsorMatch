"""This module contains a class that acts as a wrapper
around the low level Elasticsearch client.
"""

import os
from elasticsearch import Elasticsearch
from app.search.response import SearchResponse



class _ElasticsearchClient:
    """Class that is a wrapper around the low level
    elasticsearch client.
    """

    def __init__(self, hosts=None, transport_class=None, **kwargs):
        if transport_class:
            self._client = Elasticsearch(hosts, transport_class, **kwargs)
        else:
            self._client = Elasticsearch(hosts, **kwargs)

    def query_index(self, index, query):
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
        self._client.delete(index=index, id=document_id, doc_type=doc_type)

    def delete_index(self, index):
        """Delete the given index"""
        if self._client.indices.exists(index):
            self._client.indices.delete(index)




elasticsearch_client = _ElasticsearchClient(os.getenv("ELASTICSEARCH_URL"))