"""This module contains functions that are wrappers around common
Elasticsearch operations.
"""


from flask import current_app, url_for
from app.common.string_helpers import getattr_nested


class QueryType:
    """Class that contains constants the denote
    different types of Elasticsearch queries.
    """

    MATCH = "match"
    BOOL = "bool"


class SearchRequest:
    """Class to represent a search request to Elasticsearch."""

    def __init__(self, query_type):
        self.query_type = query_type

    def to_dict(self):
        pass


class ElasticsearchPagination:
    """Class that mimics the interface of Flask-SQLAlchemy's
    Pagination object. This is needed to overcome the fact that you
    cannot create a proper Pagination object when returning search results
    from Elasticsearch
    """

    def __init__(self, has_prev, has_next, prev_num, next_num, page, total, items):
        self.has_prev = has_prev
        self.has_next = has_next
        self.prev_num = prev_num
        self.next_num = next_num
        self.page = page
        self.total = total
        self.items = items

    def iter_pages(self):
        current_page = 1
        total_pages = self.total
        while total_pages > 0:
            yield current_page
            current_page += 1
            total_pages -= current_app.config["EVENTS_PER_PAGE"]

    @classmethod
    def create(cls, prev_url, next_url, total, current_page, items):
        has_prev = prev_url is not None
        has_next = next_url is not None
        prev_num = 1
        if has_prev:
            prev_num = current_page - 1
        next_num = 1
        if has_next:
            next_num = current_page + 1
        return cls(has_prev, has_next, prev_num, next_num, current_page, total, items)


def get_ids_and_num_results(search):
    """Return the ids of the documents found in the search as well as
    the number of hits.
    """
    ids = [int(hit["_id"]) for hit in search["hits"]["hits"]]
    num_results = search["hits"]["total"]["value"]
    return ids, num_results


def add_to_index(index, doc_type, model):
    """Add fields from the given model to the given index."""
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr_nested(model, field)
    current_app.elasticsearch.index(
        index=index, id=model.id, doc_type=doc_type, body=payload
    )


def remove_from_index(index, doc_type, model):
    """Remove a document in the given index based on the id
	of the given model
    """
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id, doc_type=doc_type)


def query_index(index, request, page, results_per_page):
    """Perform a date range query on the given index and return the ids of the documents
	found during the search as well as the number of matching results.
    """
    if not current_app.elasticsearch:
        return [], 0
    if request["query_type"] == QueryType.MATCH:
        search_results = execute_match_query(index, request, page, results_per_page)
    elif request["query_type"] == QueryType.BOOL:
        search_results = execute_bool_query(index, request, page, results_per_page)
    else:
        return [], 0
    return get_ids_and_num_results(search_results)


def execute_match_query(index, request, page, results_per_page):
    search_results = current_app.elasticsearch.search(
        index=index,
        body={
            "query": {"match": {request["field"]: {"query": request["query"]}}},
            "from": (page - 1) * results_per_page,
            "size": results_per_page,
        },
    )
    return search_results


def execute_bool_query(index, request, page, results_per_page):
    search_results = current_app.elasticsearch.search(
        index=index,
        body={
            "query": {
                "bool": {
                    "must": request.get("must", []),
                    "filter": request.get("filter", []),
                    "must_not": request.get("must_not", []),
                    "should": request.get("should", []),
                    **request.get("extra_params", {}),
                }
            },
            "from": (page - 1) * results_per_page,
            "size": results_per_page
        },
    )
    return search_results


def delete_index(index):
    """Delete the given index"""
    if current_app.elasticsearch:
        if current_app.elasticsearch.indices.exists(index):
            current_app.elasticsearch.indices.delete(index)


def paginate_search(model, request, endpoint, page, results_per_page):
    results, total = model.search(request, page, results_per_page)
    prev_url = None
    if page > 1:
        prev_url = url_for(endpoint, query=request["query"], page=page - 1)
    next_url = None
    if total > page * results_per_page:
        next_url = url_for(endpoint, query=request["query"], page=page + 1)
    pagination = ElasticsearchPagination.create(
        prev_url, next_url, total, page, results
    )
    data = {
        "total": total,
        "prev_url": prev_url,
        "next_url": next_url,
        "pagination": pagination,
        model.__tablename__: results
    }
    return data
