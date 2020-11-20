"""This module contains classes to represent various Elasticsearch
queries.
"""

from abc import ABC


class Query(ABC):
    """Abstract base class for queries."""

    @property
    def page(self):
        """Return the page that the search query will start at."""
        return self._query["from"]

    @property
    def results_per_page(self):
        """Return the number of results per page that the query will return."""
        return self._query["size"]

    def update_pagination(self, field, value):
        """Update the value of either the from or size pagination fields."""
        self._query["query"][field] = value

    def to_dict(self):
        """Return the match query object as a dictionary."""
        return self._query


class MatchQuery(Query):
    """Class to represent a match query."""

    def __init__(self, field, query, from_=0, size=10):
        self._query = {
            "query": {"match": {field: {"query": query}}}, "from": from_, "size": size
        }
        self.fool = None

    def update(self, field, query):
        """Update a query for a specific field."""
        self._query["query"]["match"] = {field: {"query": query}}

    


class BooleanQuery(Query):
    """Class to represent a boolean query."""

    CLAUSES = {"must", "must_not", "should", "filter"}

    def __init__(self, from_=0, size=10):
        self._query = {
            "query": {
                "bool": {"must": [], "must_not": [], "should": [], "filter": []},
            },
            "from": from_,
            "size": size,
        }

    def add(self, clause, query_type, field, query):
        """Add to the specified clause of the boolean query.
        The only valid clauses are: must, must_not, should, and filter
        """
        if clause not in self.CLAUSES:
            raise ValueError(f"{clause} is not a valid boolean query clause")
        self._query["query"]["bool"][clause].append({query_type: {field: query}})


