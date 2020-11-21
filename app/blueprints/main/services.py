"""This module contains functions that act as abtractions for opertions in
the main blueprint.
"""

from app.search import BooleanQuery, QueryType, BooleanClause


    
def create_advanced_event_search_query(form_data):
    bool_query = BooleanQuery()
    bool_query.add(
        BooleanClause.MUST, 
        QueryType.TERM,
        "event_category_id",
        {"value": form_data["category"]}
    )
    bool_query.add(
        BooleanClause.MUST,
        QueryType.MATCH,
        "venue.city",
        {"query": form_data["city"]}
    )
    bool_query.add(
        BooleanClause.MUST,
        QueryType.MATCH,
        "venue.state",
        {"query": form_data["state"]}
    )
    bool_query.add(
        BooleanClause.MUST,
        QueryType.RANGE,
        "start_datetime",
        {
            "gte": form_data["start_date"],
            "lte": form_data["end_date"],
            "format": "yyyy-MM-dd"   
        }   
    )
    bool_query.add(
        BooleanClause.MUST,
        QueryType.RANGE,
        "end_datetime",
        {
            "gte": form_data["start_date"],
            "lte": form_data["end_date"],
            "format": "yyyy-MM-dd"
        }
    )
    return bool_query
