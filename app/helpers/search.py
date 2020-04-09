"""This module contains functions that are wrappers around common
Elasticsearch operations.
"""


from flask import current_app


def add_to_index(index, doc_type, model):
    """Add fields from the given model to the given index.

	Args:
		index(str): The name of the index
		doc_type(str): The document type
		model(object): An instance of the model whose fields
			are to be added to the index
	Returns:
		None
	"""
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    current_app.elasticsearch.index(
        index=index, id=model.id, doc_type=doc_type, body=payload
    )


def remove_from_index(index, doc_type, model):
    """Remove a document in the given index based on the id
	of the given model.

	Args:
		index(str): The name of the index
		doc_type(str): The document type
		model(object): An instance of the model whose fields a
		are to be removed from the index
	Returns:
		None
	"""
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id, doc_type=doc_type)


def query_index(index, query, page, results_per_page):
    """Query the given index and return the ids of the documents
	found during the search as well as the number of matching results.

	Args:
		index(str): The name of the index
		query(str): The data to be searched for in the given index
		page(int): The page to be searched in elasticsearch
		result_per_page(int): The number of results to return per page
	Returns:
		ids(list): A list of the ids of the documents found during the search
		num_results(int): The number of search results returned
	"""
    if not current_app.elasticsearch:
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        body={
            "query": {
                "multi_match": {"query": query, "lenient": "true", "fields": ["*"]}
            },
            "from": (page - 1) * results_per_page,
            "size": results_per_page,
        },
    )
    ids = [int(hit["_id"]) for hit in search["hits"]["hits"]]
    num_results = search["hits"]["total"]["value"]
    return ids, num_results


def delete_index(index):
    """Delete the given index
    Args:
        index(str): The name of the index to be deleted.
    Returns:
        None
    """
    if current_app.elasticsearch:
        if current_app.elasticsearch.indices.exists(index):
            current_app.elasticsearch.indices.delete(index)
