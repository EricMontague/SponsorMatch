"""This module contains view functions for the main blueprint."""


from datetime import datetime
from sqlalchemy import func
from flask import (
    render_template,
    url_for,
    redirect,
    request,
    g,
    current_app
)
from flask_login import login_required, current_user
from app.blueprints.main import main
from app.blueprints.main.forms import AdvancedSearchForm, SearchForm
from app.extensions import db
from app.models import Event, Venue



class FakePagination:
    """Class that mimics the interface of Flask-SQLAlchemy's
    Pagination object. This is needed to overcome the fact that you
    cannot create a proper Pagination object when returning search results
    from Elasticsearch
    """
    def __init__(self, has_prev, has_next, prev_num, next_num, page, total):
        self.has_prev = has_prev
        self.has_next = has_next
        self.prev_num = prev_num
        self.next_num = next_num
        self.page = page
        self.total = total

    def iter_pages(self):
        current_page = 1
        total_pages = self.total
        while total_pages > 0:
            yield current_page
            current_page += 1
            total_pages -= current_app.config["EVENTS_PER_PAGE"]


   
def create_fake_pagination(prev_url, next_url, total, current_page):
    has_prev = prev_url is not None
    has_next = next_url is not None
    prev_num = 1 
    if has_prev:
        prev_num = current_page - 1
    next_num = 1
    if has_next:
        next_num = current_page + 1
    return FakePagination(has_prev, has_next, prev_num, next_num, current_page, total)
 

@main.route("/")
def index():
    """Return the home page of the application."""
    form = AdvancedSearchForm()
    page = request.args.get("page", 1, type=int)
    pagination = Event.query.filter(Event.is_ongoing() == True).paginate(
        page, per_page=current_app.config["EVENTS_PER_PAGE"], error_out=False
    )
    events = pagination.items
    return render_template(
        "main/index.html", events=events, form=form, pagination=pagination
    )



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
        return redirect(url_for("main.index"))
    endpoint = "main.search"
    page = request.args.get("page", 1, type=int)
    events, total = Event.search(
        g.search_form.query.data, page, current_app.config["EVENTS_PER_PAGE"]
    )
    if events:
        events = [event for event in events if event.is_ongoing()]
    prev_url = None
    if page > 1:
        prev_url = url_for("main.search", query=g.search_form.query.data, page=page - 1)
    next_url = None
    if total > page * current_app.config["EVENTS_PER_PAGE"]:
        next_url = url_for("main.search", query=g.search_form.query.data, page=page + 1)
    fake_pagination = create_fake_pagination(prev_url, next_url, total, page)
    return render_template(
        "main/search.html",
        events=events,
        endpoint=endpoint,
        pagination=fake_pagination,
        prev_url=prev_url,
        next_url=next_url,
    )




