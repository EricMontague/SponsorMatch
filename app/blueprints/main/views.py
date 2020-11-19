"""This module contains view functions for the main blueprint."""


from datetime import datetime
from flask import render_template, url_for, redirect, request, g, current_app
from flask_login import login_required, current_user
from app.blueprints.main import main, services
from app.blueprints.main.forms import AdvancedSearchForm, SearchForm
from app.extensions import db
from app.models import Event, Venue
from app.common import paginate_search, QueryType


@main.route("/")
def index():
    """Return the home page of the application."""
    form = AdvancedSearchForm()
    page = request.args.get("page", 1, type=int)
    pagination = Event.query.filter(Event.is_ongoing() == True).paginate(
        page, per_page=current_app.config["EVENTS_PER_PAGE"], error_out=False
    )

    events = [(event.main_image, event) for event in pagination.items]
    return render_template(
        "main/index.html", events=events, form=form, pagination=pagination
    )


@main.route("/advanced-search", methods=["GET"])
def advanced_search():
    """View function to handle queries from the advanced search form
    on the home page."""
    search_endpoint = "main.advanced_search"
    form = AdvancedSearchForm()
    page = request.args.get("page", 1, type=int)
    form_data = form.data
    state_id = form.state.data
    form_data["state"] = AdvancedSearchForm.convert_choice_to_value(form.state.data, "STATES")
    search_request = services.create_advanced_event_search_request(form_data)
    results = paginate_search(
        Event,
        search_request,
        search_endpoint,
        page,
        current_app.config["EVENTS_PER_PAGE"],
    )
    fragment = f'''
        query={state_id}
        &{form_data["city"]}
        &{form_data["start_date"]}
        &{form_data["end_date"]}
        &{form_data["category"]}&
    '''
    events = [
        (event.main_image, event)
        for event in results["events"]
    ]
    print(events)
    return render_template(
        "main/search.html",
        events=events,
        endpoint=search_endpoint,
        pagination=results["pagination"],
        prev_url=results["prev_url"],
        next_url=results["next_url"],
        fragment=fragment,
    )
    
    


@main.route("/search")
def search():
    """Return search results."""
    search_endpoint = "main.search"
    page = request.args.get("page", 1, type=int)
    search_request = services.create_simple_event_search_request(
        g.search_form.query.data, "title"
    )
    results = paginate_search(
        Event,
        search_request,
        search_endpoint,
        page,
        current_app.config["EVENTS_PER_PAGE"],
    )
    events = [
        (event.main_image, event)
        for event in results["events"]
    ]
    return render_template(
        "main/search.html",
        events=events,
        endpoint=search_endpoint,
        pagination=results["pagination"],
        prev_url=results["prev_url"],
        next_url=results["next_url"],
        fragment=f"query={g.search_form.query.data}&",
    )

