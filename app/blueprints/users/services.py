"""This module contains functions that serve as abstractions for
operations in the user blueprint.
"""
from app.models import EventStatus, SponsorshipStatus, Event, Sponsorship


def get_user_profile_data(user, profile_type, tab):
    # If users is an event organizer
    if user.can(Permission.CREATE_EVENT) or user.is_administrator():
        tab = "live_event"
        if past == 1:
            tab = "past_event"
            pagination = services.get_user_events_by_status(
                EventStatus.PAST,
                user,
                page,
                current_app.config["EVENTS_PER_PAGE"]
            )
            
        else:  # query live events
            pagination = services.get_user_events_by_status(
                EventStatus.Live,
                user,
                page,
                current_app.config["EVENTS_PER_PAGE"]
            )
            
    else:  # user is a sponsor
        tab = "current_sponsorship"
        if past == 1:
            tab = "past_sponsorship"
            pagination = services.get_user_events_by_status(
                Sponsorship.PAST,
                user,
                page,
                current_app.config["EVENTS_PER_PAGE"]
            )
        else:  # current sponsored events
            pagination = services.get_user_events_by_status(
                Sponsorship.Live,
                user,
                page,
                current_app.config["EVENTS_PER_PAGE"]
            )
    return pagination

def get_user_events_by_status(status, user, page, results_per_page):
    """Return a pagination object containing events based on the given
    status.
    """
    if status == EventStatus.PAST:
        query = Event.query.filter(Event.user_id == user.id, Event.has_ended() == True)
    elif status == EventStatus.LIVE:
        query = Event.query.filter(Event.user_id == user.id, Event.is_ongoing() == True)

    pagination = query.paginate(
        page=page, per_page=results_per_page, error_out=False
    )
    return pagination


def get_user_sponsored_events_by_status(status, user, page, results_per_page):
    """Return a pagination object containing sponsorships based on
    the given status.
    """
    if status == SponsorshipStatus.PAST:
        query = (
            Event.query.join(Sponsorship, Sponsorship.event_id == Event.id)
            .filter(Event.is_past() == True)
            .filter(
                Sponsorship.sponsor_id == user.id, Sponsorship.is_pending() == False
            )
        )
    elif status == SponsorshipStatus.CURRENT:
        query = (
            Event.query.join(Sponsorship, Sponsorship.event_id == Event.id)
            .filter(Event.is_ongoing() == True)
            .filter(
                Sponsorship.sponsor_id == user.id, Sponsorship.is_pending() == False
            )
        )
    pagination = query.paginate(
        page=page, per_page=results_per_page, error_out=False
    )
    return pagination