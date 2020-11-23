"""This module contains view functions for the main blueprint."""


from datetime import datetime
from flask import render_template, url_for, redirect, request, g, current_app
from flask_login import login_required, current_user
from app.blueprints.main import main, services
from app.blueprints.main.forms import AdvancedSearchForm, SearchForm
from app.extensions import db
from app.models import Event, Venue
from app.search import MatchQuery


@main.route("/")
def index():
    """Return the home page of the application."""
    form = AdvancedSearchForm()
    page = request.args.get("page", 1, type=int)
    pagination = Event.query.filter(Event.is_ongoing() == True).paginate(
        page, per_page=current_app.config["EVENTS_PER_PAGE"], error_out=False
    )
    events = [(event.main_image(), event) for event in pagination.items]
    return render_template(
        "main/index.html", events=events, form=form, pagination=pagination
    )


@main.route("/advanced-search")
def advanced_search():
    """View function to handle queries from the advanced search form
    on the home page."""
    search_endpoint = "main.advanced_search"
    form = AdvancedSearchForm()
    page = request.args.get("page", 1, type=int)
    if form.validate():
        form_data = form.data
        state_id = form.state.data
        form_data["state"] = AdvancedSearchForm.convert_choice_to_value(form.state.data, "STATES")
        search_query = services.create_advanced_event_search_query(form_data)
        search_response, pagination = current_app.sqlalchemy_search_middleware.search(
            Event, search_query
        )
        fragment = (
            f"state={state_id}"
            + f"&city={form_data['city']}"
            + f"&start_date={form_data['start_date']}"
            + f"&end_date={form_data['end_date']}"
            + f"&category={form_data['category']}&"
        )
        events = [
            (event.main_image(), event)
            for event in pagination.items
        ]
        
        return render_template(
            "main/search.html",
            events=events,
            endpoint=search_endpoint,
            pagination=pagination,
            fragment=fragment,
        )
    pagination = Event.query.filter(Event.is_ongoing() == True).paginate(
        page, per_page=current_app.config["EVENTS_PER_PAGE"], error_out=False
    ) 
    events = [(event.main_image(), event) for event in pagination.items]
    return render_template(
        "main/index.html", events=events, form=form, pagination=pagination
    )
    
    


@main.route("/search")
def search_events_by_title():
    """Return search results for searching for events
    by title.
    """
    search_endpoint = "main.search_events_by_title"
    page = request.args.get("page", 1, type=int)
    match_query = MatchQuery("title", g.search_form.query.data, from_=page-1)
    fragment = f"query={g.search_form.query.data}&"
    search_response, pagination = current_app.sqlalchemy_search_middleware.search(
        Event, match_query
    )
    events = [
        (event.main_image(), event)
        for event in pagination.items
    ]
    return render_template(
        "main/search.html",
        events=events,
        endpoint=search_endpoint,
        pagination=pagination,
        fragment=fragment
    )

