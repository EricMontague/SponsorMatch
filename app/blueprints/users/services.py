"""This module contains functions that serve as abstractions for
operations in the user blueprint.
"""

from app.models import EventStatus, SponsorshipStatus, Event, Sponsorship, User, Permission


class InvalidUserType(Exception):
    pass


class PhotoUploadError(Exception):
    pass


class PhotoNotFoundError(Exception):
    pass


def get_user_profile_data(company, page, results_per_page, past):
    user = User.query.filter_by(company=company).first_or_404()
    if user.can(Permission.CREATE_EVENT) or user.is_administrator():
        return get_event_organizer_profile_data(user, page, results_per_page, past)
    return get_sponsor_profile_data(user, page, results_per_page, past)


def get_event_organizer_profile_data(user, page, results_per_page, past):
    
    tab = "live_event"
    if past == 1:
        tab = "past_event"
        pagination = get_user_events_by_status(
            EventStatus.PAST, user, page, results_per_page
        )
    else:  # query live events
        pagination = get_user_events_by_status(
            EventStatus.LIVE, user, page, results_per_page
        )
    profile_data = {"user": user, "pagination": pagination, "tab": tab}
    return profile_data


def get_sponsor_profile_data(user, page, results_per_page, past):
    tab = "current_sponsorship"
    if past == 1:
        tab = "past_sponsorship"
        pagination = get_user_sponsored_events_by_status(
            SponsorshipStatus.PAST, user, page, results_per_page
        )
    else:  # current sponsored events
        pagination = get_user_sponsored_events_by_status(
            SponsorshipStatus.CURRENT, user, page, results_per_page
        )
    profile_data = {"user": user, "pagination": pagination, "tab": tab}
    return profile_data


def get_user_events_by_status(status, user, page, results_per_page):
    """Return a pagination object containing events based on the given
    status.
    """
    if status == EventStatus.PAST:
        query = Event.query.filter(Event.user_id == user.id, Event.has_ended() == True)
    elif status == EventStatus.LIVE:
        query = Event.query.filter(Event.user_id == user.id, Event.is_ongoing() == True)

    pagination = query.paginate(page=page, per_page=results_per_page, error_out=False)
    return pagination


def get_user_sponsored_events_by_status(status, user, page, results_per_page):
    """Return a pagination object containing sponsorships based on
    the given status.
    """
    if status == SponsorshipStatus.PAST:
        query = (
            Event.query.join(Sponsorship, Sponsorship.event_id == Event.id)
            .filter(Event.is_past() == True)
            .filter(Sponsorship.sponsor_id == user.id)
        )
    elif status == SponsorshipStatus.CURRENT:
        query = (
            Event.query.join(Sponsorship, Sponsorship.event_id == Event.id)
            .filter(Event.is_ongoing() == True)
            .filter(Sponsorship.sponsor_id == user.id)
        )
    pagination = query.paginate(page=page, per_page=results_per_page, error_out=False)
    return pagination


def upload_user_profile_photo(user, image, file_uploader, os):
    """Upload the given photo to the filesystem."""
    filename = file_uploader.save(image)
    if user.profile_photo_path is not None:  # updating profile photo
        try:
            # remove current image in the image folder
            os.remove(user.profile_photo_path)
        except OSError:
            raise PhotoUploadError("Upload was unsuccessful, please try again.")
    user.profile_photo_path = file_uploader.path(filename)


def delete_user_profile_photo(path, current_user, os):
    """Delete the given user's profile photo."""
    if current_user.is_administrator():  # admin trying to delete a user's photo
        user = User.query.filter_by(profile_photo_path=path).first_or_404()
    else:  # user trying to delete their own photo
        user = current_user._get_current_object()
    if os.path.exists(path):
        os.remove(path)
        user.profile_photo_path = None
    else:
        raise FileNotFoundError("User profile photo not found")
