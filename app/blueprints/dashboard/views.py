"""This module contains view functions for the dashboard blueprint."""


from datetime import datetime
from flask_login import login_required, current_user
from app.blueprints.dashboard import dashboard
from app.extensions import db
from flask import render_template, url_for, redirect, abort
from app.blueprints.dashboard.forms import DropdownForm
from app.helpers import permission_required, admin_required
from app.models import (
    User,
    Role,    
    Permission,
    EventStatus,
    SponsorshipStatus
)


# need to add ajax requests in template for this route
@dashboard.route("/events/<status>")
@login_required
@permission_required(Permission.CREATE_EVENT)
def events_dashboard(status):
    """Return a page that allows a user to see all of their events in 
    one place.
    """
    choices = [(1, "All"), (2, "Live"), (3, "Past"), (4, "Draft")]
    dropdown_form = DropdownForm(choices)
    user = current_user._get_current_object()
    if status == EventStatus.LIVE:
        events = [event for event in user.events if event.is_ongoing()]
    elif status == EventStatus.DRAFT:
        events = [event for event in user.events if event.is_draft()]
    elif status == EventStatus.PAST:
        events = [event for event in user.events if event.has_ended()]
    else:
        events = user.events.all()

    # set default value equal to status
    reverse_choices = {choice.lower(): number for number, choice in choices}
    dropdown_form.options.data = reverse_choices[status]
    return render_template(
        "dashboard/events_dashboard.html",
        user=user,
        events=events,
        dropdown_form=dropdown_form,
        datetime=datetime,
    )


@dashboard.route("/sponsorships/<status>")
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def sponsorships_dashboard(status):
    """return a page that allows a sponsor to view current
    and past sponsorships."""
    choices = [(1, "All"), (2, "Current"), (3, "Past")]
    dropdown_form = DropdownForm(choices)
    user = current_user._get_current_object()
    if status == SponsorshipStatus.CURRENT:
        sponsorships = [
            sponsorship
            for sponsorship in user.sponsorships
            if not sponsorship.is_pending() and sponsorship.is_current()
        ]
    elif status == SponsorshipStatus.PAST:
        sponsorships = [
            sponsorship
            for sponsorship in user.sponsorships
            if not sponsorship.is_pending() and sponsorship.is_past()
        ]
    else:
        sponsorships = [
            sponsorship
            for sponsorship in user.sponsorships
            if not sponsorship.is_pending()
        ]

    reverse_choices = {choice.lower(): number for number, choice in choices}
    dropdown_form.options.data = reverse_choices[status]
    return render_template(
        "dashboard/sponsorships_dashboard.html",
        sponsorships=sponsorships,
        dropdown_form=dropdown_form,
    )


@dashboard.route("/admin/<role_name>")
@login_required
@admin_required
def admin_dashboard(role_name):
    """Return a page that allows a user with administrator priveleges
    to manage the website."""
    roles = [(1, "All"), (2, "Sponsor"), (3, "Event Organizer"), (4, "Administrator")]
    dropdown_form = DropdownForm(roles)
    if role_name == "all":
        users = User.query.all()
    else:
        role = Role.query.filter_by(name=role_name.title()).first_or_404()
        users = User.query.filter_by(role=role).all()
    reverse_roles = {role_name.lower(): number for number, role_name in roles}
    dropdown_form.options.data = reverse_roles[role_name]
    return render_template(
        "dashboard/admin_dashboard.html", users=users, dropdown_form=dropdown_form
    )
