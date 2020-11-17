"""This module contains functions that act as abtractions for opertions in
the main blueprint.
"""

from sqlalchemy import func
from app.models import Event, Venue
from flask import url_for



def create_advanced_search_request(form_data):
    search_request = {
        "must": [
            {
                "term": {
                    "event_category_id": {
                        "value": form_data["event_category"]
                    }
                }
            },
            {
                "match": {
                    "city": {
                        "query": form_data["city"]
                    }
                }
            },
            {
                "match": {
                    "state": {
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