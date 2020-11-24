"""This module contains a search mixin class to connect SQLAlchemy models to Elasticsearch."""


import math
from app.search.pagination import ElasticsearchPagination
from app.search.utils import getattr_nested


class FlaskSQLAlchemyMiddleware:
    """Class that acts as middleware between FlaskSQLAlchemy and Elasticsearch."""

    def __init__(self, elasticsearch_client, database):
        self._elasticsearch_client = elasticsearch_client
        self._database = database

    def search(self, model, search_query):
        """Perform a search on Elasticsearch and return the corresponding objects
        as well as the number of results.
        """
        response = self._elasticsearch_client.query_index(
            model.__tablename__, search_query
        )
        sql_query = self._create_query(model, response)
        pagination = self._create_pagination(response, sql_query)
        return response, pagination

    def _create_query(self, model, response):
        """Return the results from the search query as a SQLAlchemy query object"""
        if response.total == 0:
            return model.query.filter_by(id=0)
        whens = []
        for index, id_ in enumerate(response.document_ids):
            whens.append((id_, index))
        # order by + case statement used to preserve the order of the results
        # essentially sorts the output using the index as the key
        # https://stackoverflow.com/questions/6332043/sql-order-by-multiple-values-in-specific-order/6332081#6332081
        return model.query.filter(model.id.in_(response.document_ids)).order_by(
            self._database.case(whens, value=model.id)
        )

    def _create_pagination(self, response, query):
        """Create and return an ElasticsearchPagination object."""
        num_pages = math.ceil(response.total / response.results_per_page)
        if response.total == 0 or num_pages == 1:
            has_prev = False
            has_next = False
        else:
            has_prev = response.page > 0
            has_next = response.page < num_pages - 1
        pagination = ElasticsearchPagination.create(
            has_prev,
            has_next,
            response.total,
            response.page + 1,
            response.results_per_page,
            query,
        )
        return pagination

    @staticmethod
    def extract_searchable_fields(model):
        """Return a dictionary containing all of the 
        searchable fields in a sqlalchemy model.
        """
        payload = {}
        if not hasattr(model, "__searchable__"):
            return payload
        for field in model.__searchable__:
            payload[field] = getattr_nested(model, field)
        payload["id"] = model.id
        payload["index"] = model.__tablename__
        payload["doc_type"] = model.__doctype__
        return payload

    def before_commit(self, session):
        """Method to be called before any commits to the database. Stores all new
        objects to be added to, modified, and deleted from the database to a dictionaty
        that will persist after the commit.
        """
        extract_fields = FlaskSQLAlchemyMiddleware.extract_searchable_fields
        session._changes = {
            "add": [extract_fields(model) for model in session.new],
            "update": [extract_fields(model) for model in session.dirty],
            "delete": [extract_fields(model) for model in session.deleted],
        }

    def after_commit(self, session):
        """Method to be called after any changes are commited to the database.
        Iterates over the changes dictionary stored in the session and 
        performs the necessary actions on Elasticsearch to make sure that both have the 
        same data.
        """
        for payload in session._changes["add"]:
            if payload:
                self._elasticsearch_client.add_to_index(
                    payload["index"], payload["doc_type"], payload["id"], payload
                )
        for payload in session._changes["update"]:
            if payload:
                self._elasticsearch_client.add_to_index(
                    payload["index"], payload["doc_type"], payload["id"], payload
                )
        for payload in session._changes["delete"]:
            if payload:
                self._elasticsearch_client.remove_from_index(
                    payload["index"], payload["doc_type"], payload["id"]
                )
        self._changes = {}

    def reindex(self, model):
        """Refresh an index with all of the data from this model's table."""
        for query in model.query:
            self._elasticsearch_client.add_to_index(
                model.__tablename__, model.__doctype__, query
            )

