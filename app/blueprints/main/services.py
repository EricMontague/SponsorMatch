"""This module contains functions that act as abtractions for opertions in
the main blueprint.
"""

from sqlalchemy import func
from app.models import Event, Venue
from flask import url_for


def get_live_events(results_per_page):
    """"Return a pagination object containing events that are 'live'.
    A live a event is an event that has been published and that has not
    yet ended.
    """
    pagination = Event.query.filter(Event.is_ongoing() == True).paginate(
        page, per_page=results_per_page, error_out=False
    )
    return pagination

def build_event_search_query(state, start_date, end_date):
    """Return a query that represents a join between the 
    events and venues tables based on search criteria provided.
    """
    query = (
        Event.query.join(Venue, Venue.id == Event.venue_id)
        .filter(Venue.state == state)
        .filter(
            func.Date(Event.start_datetime) >= start_date,
            func.Date(Event.start_datetime) <= end_date,
            Event.is_ongoing() == True,
        )
    )
    return query


def create_prev_and_next_urls(pagination, endpoint):
    """Return the previous and next urls for the given endpoint."""
    prev_url = None
    if pagination.has_prev:
        prev_url = url_for(endpoint, page=pagination.prev_num)
    next_url = None
    if pagination.has_next:
        next_url = url_for(endpoint, page=pagination.next_num)
    return prev_url, next_url


def execute_advanced_event_search(query, form_data, endpoint, page, results_per_page):
    """Return paginated search results from the database."""
    # user selected all categories an omitted city
    if form_data["category"] == 0 and form_data["city"] == "":
        pagination = query.paginate(
            page, per_page=results_per_page, error_out=False
        )
    # user selected all categories, but typed in a specific city
    elif form_data["category"] == 0:
        pagination = query.filter(Venue.city == form_data["city"]).paginate(
            page, per_page=results_per_page, error_out=False
        )
    # user selected a specific category, but omitted the city
    elif form_data["city"] == "":
        pagination = query.filter(
            Event.event_category_id == form_data["category"]
        ).paginate(
            page, per_page=results_per_page, error_out=False
        )
    # user filled out the form with complete specificity
    else:
        pagination = (
            query.filter(Venue.city == form_data["city"])
            .filter(Event.event_category_id == form_data["category"])
            .paginate(
                page,
                per_page=results_per_page,
                error_out=False,
            )
        )
    prev_url, next_url = create_prev_and_next_urls(pagination, endpoint)
    results = {
        "prev_url": prev_url,
        "next_url": next_url,
        "pagination": pagination
    }
    return results