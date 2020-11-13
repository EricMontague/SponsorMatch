"""This module contains a search mixin class to connect models to Elasticsearch."""


from app.extensions import db
from app.common.search import add_to_index, remove_from_index, query_index, delete_index


class SearchableMixin:
    """Mixin class that extends the functionality of a model to be able
    to perform searches and updates on Elasticsearch.
    """

    @classmethod
    def search(cls, query, page, results_per_page):
        """Perform a search on Elasticsearch and return the corresponding objects
        as well as the number of results.
        """
        ids, total = query_index(cls.__tablename__, query, page, results_per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        whens = []
        for index, id_ in enumerate(ids):
            whens.append((id_, index))
        # order by + case statement used to preserve the order of the results
        # essentially sorts the output using the index as the key
        return (
            cls.query.filter(cls.id.in_(ids)).order_by(db.case(whens, value=cls.id)),
            total,
        )

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

    @classmethod
    def after_commit(cls, session):
        """Method to be called after any commits to the database. Iterates over the 
        changes dictionary stored in the session and performs the necessary actions on 
        Elasticsearch to make sure that both have the same data.
        """
        for obj in session._changes["add"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj.__doctype__, obj)
        for obj in session._changes["update"]:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj.__doctype__, obj)
        for obj in session._changes["delete"]:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj.__doctype__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        """Refresh an index with all of the data from this model's table."""
        for obj in cls.query:
            add_to_index(cls.__tablename__, cls.__doctype__, obj)

    @classmethod
    def delete_index(cls, index=None):
        """Delete the related index in Elasticsearch."""
        if index is None:
            index = cls.__tablename__
        delete_index(index)


db.event.listen(db.session, "before_commit", SearchableMixin.before_commit)
db.event.listen(db.session, "after_commit", SearchableMixin.after_commit)

