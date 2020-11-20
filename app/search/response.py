"""This module contains a class which represents a response
from an elasticsearch query.
"""


class SearchResponse:
    """Class to represent a response from an elasticsearch
    query.
    """

    def __init__(self, results, query):
        self._results = results
        self.query = query
        self.total = results["hits"]["total"]["value"]
        self.hits = results["hits"]["hits"]
        self.page = query.page
        self.results_per_page = query.results_per_page
        self.took = results["took"]
        self.timed_out = False
        self.shards = results["_shards"]
        self.max_score = results["hits"]["max_score"]
        self.document_ids = self._extract_document_ids(results["hits"]["hits"])


    def _extract_document_ids(self, hits):
        """Return a list of ids from the documents matched in the search query."""
        return [int(hit["_id"]) for hit in hits]

    def to_dict__(self):
        """Return the elasticsearch response as a dictionary."""
        return self._results

