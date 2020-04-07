"""This module contains view functions for the main blueprint."""


from datetime import datetime
from sqlalchemy import func
from flask import (
    render_template,
    url_for,
    redirect,
    request,
    g,
    current_app,
    make_response
)
from flask_login import login_required, current_user
from app.blueprints.main import main
from app.blueprints.main.forms import AdvancedSearchForm, SearchForm
from app.extensions import db
from app.models import Event, Venue
   
 
@main.route("/")
def index():
    """Return the home page of the application."""
    form = AdvancedSearchForm()
    near_you = False
    if current_user.is_authenticated:
        near_you = bool(request.cookies.get("near_you", ""))
    if near_you:
        query = current_user.nearby_events
    else:
        query = Event.query
    page = request.args.get("page", 1, type=int)
    pagination = query.filter(Event.is_ongoing() == True).paginate(
        page, per_page=current_app.config["EVENTS_PER_PAGE"], error_out=False
    )
    events = pagination.items
    return render_template(
        "main/index.html", events=events, form=form, pagination=pagination
    )


# need to add cookie functionality for homepage later
@main.route("/all")
@login_required
def show_all():
    """Remove near_you cookie from user's browser to an empty string"""
    response = make_response(redirect(url_for(".index")))
    response.set_cookie("near_you", "", max_age=30 * 24 * 60 * 60)  # 30 days
    return response


# need to add cookie functionality for homepage later
@main.route("/near-you")
@login_required
def near_you():
    """Set a near_you cookie in the user's browser"""
    response = make_response(redirect(url_for(".index")))
    response.set_cookie("near_you", "1", max_age=30 * 24 * 60 * 60)  # 30 days
    return response


@main.route("/", methods=["POST"])
def advanced_search():
    """View function to handle queries from the advanced search form
    on the home page."""
    endpoint = "main.advanced_search"
    form = AdvancedSearchForm()
    page = request.args.get("page", 1, type=int)
    if form.validate_on_submit():
        state = AdvancedSearchForm.choice_value(form.state.data, "STATES")
        query = (
            Event.query.join(Venue, Venue.id == Event.venue_id)
            .filter(Venue.state == state)
            .filter(
                func.Date(Event.start_datetime) >= form.start_date.data,
                func.Date(Event.start_datetime) <= form.end_date.data,
                Event.is_ongoing() == True
            )
        )
        # user selected all categories an omitted city
        if form.category.data == 0 and form.city.data == "":
            pagination = query.paginate(
                page, per_page=current_app.config["EVENTS_PER_PAGE"], error_out=False
            )
        # user selected all categories, but typed in a specific city
        elif form.category.data == 0:
            pagination = query.filter(Venue.city == form.city.data).paginate(
                page, per_page=current_app.config["EVENTS_PER_PAGE"], error_out=False
            )
        # user selected a specific category, but omitted the city
        elif form.city.data == "":
            pagination = query.filter(
                Event.event_category_id == form.category.data
            ).paginate(
                page, per_page=current_app.config["EVENTS_PER_PAGE"], error_out=False
            )
        # user filled out the form with complete specificity
        else:
            pagination = (
                query.filter(Venue.city == form.city.data)
                .filter(Event.event_category_id == form.category.data)
                .paginate(
                    page,
                    per_page=current_app.config["EVENTS_PER_PAGE"],
                    error_out=False,
                )
            )
        events = pagination.items
        prev_url = None
        if pagination.has_prev:
            prev_url = url_for("main.search", page=pagination.prev_num)
        next_url = None
        if pagination.has_next:
            next_url = url_for("main.search", page=pagination.next_num)
        return render_template(
            "main/search.html", events=events, prev_url=prev_url, next_url=next_url
        )
    pagination = Event.query.filter(Event.is_ongoing() == True).paginate(
        page, per_page=current_app.config["EVENTS_PER_PAGE"], error_out=False
    )
    events = pagination.items
    return render_template(
        "main/index.html", events=events, form=form, pagination=pagination
    )
    
    
@main.route("/search")
def search():
    """Return search results."""
    if not g.search_form.validate():
        return redirect("main.index")
    endpoint = "main.search"
    page = request.args.get("page", 1, type=int)
    events, total = Event.search(
        g.search_form.query.data, page, current_app.config["EVENTS_PER_PAGE"]
    )
    live_events = None
    if events:
        events = [event for event in events if event.is_ongoing()]
    prev_url = None
    if page > 1:
        prev_url = url_for("main.search", query=g.search_form.query.data, page=page - 1)
    next_url = None
    if total > page * current_app.config["EVENTS_PER_PAGE"]:
        next_url = url_for("main.search", query=g.search_form.query.data, page=page + 1)
    return render_template(
        "main/search.html",
        events=events,
        endpoint=endpoint,
        prev_url=prev_url,
        next_url=next_url,
    )




