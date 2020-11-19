"""This module contains functions that act as abtractions for opertions in
the main blueprint.
"""

from sqlalchemy import func
from app.models import Event, Venue
from flask import url_for
from app.common import QueryType



def create_simple_event_search_request(query, field):
    search_request = {
        "query": query,
        "field": field,
        "query_type": QueryType.MATCH,
    }
    return search_request



def create_advanced_event_search_request(form_data):
    search_request = {
        "query_type": QueryType.BOOL,
        "must": [
            {
                "term": {
                    "event_category_id": {
                        "value": form_data["category"]
                    }
                }
            },
            {
                "match": {
                    "venue.city": {
                        "query": form_data["city"]
                    }
                }
            },
            {
                "match": {
                    "venue.state": {
                        "query": form_data["state"]
                    }
                }
            },
            {
                "range": {
                    "start_datetime": {
                        "gte": form_data["start_date"],
                        "lte": form_data["start_date"],
                        "format": "yyyy-MM-dd"
                    }
                }
            },
            {
                "range": {
                    "end_datetime": {
                        "gte": form_data["end_date"],
                        "lte": form_data["end_date"],
                        "format": "yyyy-MM-dd"
                    }
                }
            },
        ]
    }
    return search_request