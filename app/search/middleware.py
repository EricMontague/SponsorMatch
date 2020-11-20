"""This module contains a search mixin class to connect SQLAlchemy models to Elasticsearch."""


import math
from app.extensions import db
from app.search.client import elasticsearch_client
from app.search.pagination import ElasticsearchPagination
from flask import url_for


class FlaskSQLAlchemyMiddleware:
    """Class that acts as middleware between FlaskSQLAlchemy and Elasticsearch."""

    def __init__(self, elasticsearch_client):
        self._elasticsearch_client = elasticsearch_client

    def search(self, model, search_query):
        """Perform a search on Elasticsearch and return the corresponding objects
        as well as the number of results.
        """
        response = self._elasticsearch_client.query_index(model.__tablename__, search_query)
        sql_query = self._create_query(model, response)
        pagination = self._create_pagination(response, sql_query)
        return response, pagination

    def _create_query(self, model, response):
        """Return the results from the search query as a SQLAlchemy query object"""
        if response.total == 0:
            return model.query.filter_by(id=0), 0
        whens = []
        for index, id_ in enumerate(response.document_ids):
            whens.append((id_, index))
        # order by + case statement used to preserve the order of the results
        # essentially sorts the output using the index as the key
        # https://stackoverflow.com/questions/6332043/sql-order-by-multiple-values-in-specific-order/6332081#6332081
        return (
            model.query.filter(model.id.in_(response.document_ids)).order_by(
                db.case(whens, value=model.id)
            )
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
          has_prev, has_next, response.total, response.page, response.results_per_page, query
        )
        return pagination

    @classmethod
    def before_commit(cls, session):
        """Method to be called before any commits to the database. Stores all new
        objects to be added to, modified, and deleted from the database to a dictionaty
        that will persist after the commit.
        """
        session._changes = {
            "add": list(session.new),
            "update": list(session.dirty),
            "delete": list(session.deleted),
        }

    def after_commit(self, session):
        """Method to be called after any commits to the database. Iterates over the 
        changes dictionary stored in the session and performs the necessary actions on 
        Elasticsearch to make sure that both have the same data.
        """
        for obj in session._changes["add"]:
            if hasattr(obj, "__searchable___"):
                self._elasticsearch_client.add_to_index(
                    obj.__tablename__, obj.__doctype__, obj
                )
        for obj in session._changes["update"]:
            if hasattr(obj, "__searchable___"):
                self._elasticsearch_client.add_to_index(
                    obj.__tablename__, obj.__doctype__, obj
                )
        for obj in session._changes["delete"]:
            if hasattr(obj, "__searchable___"):
                self._elasticsearch_client.remove_from_index(
                    obj.__tablename__, obj.__doctype__, obj
                )
        session._changes = None

    def reindex(self, model):
        """Refresh an index with all of the data from this model's table."""
        for obj in model.query:
            self._elasticsearch_client.add_to_index(
                model.__tablename__, model.__doctype__, obj
            )

    def delete_index(self, index):
        """Delete the related index in Elasticsearch."""
        self._elasticsearch_client.delete_index(index)


sqlalchemy_search_middleware = FlaskSQLAlchemyMiddleware(elasticsearch_client)
db.event.listen(db.session, "before_commit", FlaskSQLAlchemyMiddleware.before_commit)
db.event.listen(db.session, "after_commit", sqlalchemy_search_middleware.after_commit)

