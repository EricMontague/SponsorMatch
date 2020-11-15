"""This module contains view functions for the main blueprint."""


from datetime import datetime
from flask import render_template, url_for, redirect, request, g, current_app
from flask_login import login_required, current_user
from app.blueprints.main import main, services
from app.blueprints.main.forms import AdvancedSearchForm, SearchForm
from app.extensions import db
from app.models import Event, Venue
from app.common import paginate_search


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


@main.route("/", methods=["POST"])
def advanced_search():
    """View function to handle queries from the advanced search form
    on the home page."""
    search_endpoint = "main.advanced_search"
    form = AdvancedSearchForm()
    page = request.args.get("page", 1, type=int)
    if form.validate_on_submit():
        state = AdvancedSearchForm.convert_choice_to_value(form.state.data, "STATES")
        query = services.build_event_search_query(
            state, form.start_date.data, form.end_date.data
        )
        form_data = {"category": form.category.data, "city": form.city.data}
        results = services.execute_advanced_event_search(
            query,
            form_data,
            search_endpoint,
            page,
            current_app.config["EVENTS_PER_PAGE"],
        )
        return render_template(
            "main/search.html",
            events=results["pagination"].items,
            prev_url=results["prev_url"],
            next_url=results["next_url"],
            pagination=results["pagination"],
        )
    pagination = services.get_live_events(current_app.config["EVENTS_PER_PAGE"])
    events = pagination.items
    if events:
        events = [
            (event.main_image, event) 
            for event in events if event.is_ongoing()
        ]
    return render_template(
        "main/index.html", events=events, form=form, pagination=pagination
    )


@main.route("/search")
def search():
    """Return search results."""


    endpoint = "main.search"
    page = request.args.get("page", 1, type=int)
    results = paginate_search(
        Event,
        g.search_form.query.data,
        "main.search",
        page,
        current_app.config["EVENTS_PER_PAGE"],
    )
    events = results["pagination"].items
    # Filter for live events only
    if events:
        events = [
            (event.main_image, event) 
            for event in events if event.is_ongoing()
        ]
    return render_template(
        "main/search.html",
        events=events,
        endpoint=endpoint,
        pagination=results["pagination"],
        prev_url=results["prev_url"],
        next_url=results["next_url"],
    )

