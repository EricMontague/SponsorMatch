"""This module contains functions that serve to abstract operations
in event blueprint."""

from datetime import datetime
from flask import url_for
from http import HTTPStatus
from app.models import (
    Event, 
    Package, 
    ImageType, 
    Image, 
    EventCategory, 
    EventType
)
from app.blueprints.events.forms import CreateEventForm


def save_misc_images(images, event, file_uploader, db_session):
    """Store all of the images for the given event in the
    database.
    """
    image_type = ImageType.query.filter_by(name="Misc").first()
    for data in images:
        filename = file_uploader.save(data)
        image = Image(
            path=file_uploader.path(filename), image_type=image_type, event=event
        )
        db_session.add(image)


def save_event_main_image(images, event, file_uploader, db_session):
    """Store the given main image for the event in the database."""
     filename = images.save(images)
    image_type = ImageType.query.filter_by(name="Main Event Image").first()
    image = Image(path=file_uploader.path(filename), image_type=image_type, event=event)
    db_session.add(image)


def validate_order(id, data, user):
    """Validate the request parameters from the user for the
    place order route. Returns the packages the user requested
    if validation is successful, else it returns a dictionary
    containing an error message to show to the user.
    """
    event = Event.query.get_or_404(id)
    if not data:
        return {"message": "Request missing JSON body"}
    if "ids" not in data:
        return {"message": "'Ids' field missing from request"}
    packages = []
    for package_id in data["ids"]:
        package = Package.query.get_or_404(package_id)
        if user.has_purchased(package):
            return {
                "message": "You cannot purchase a package more than once",
                "url": url_for("events.event", id=event.id),
            }
        packages.append(package)
    return {"packages": packages}



def populate_create_event_form(form, venue, event):
    """Helper function to population the Create Event Form."""
    # Venue info
    venue = event.venue
    form.venue_name.data = venue.name
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = CreateEventForm.convert_choice_to_id(venue.state, "STATES")
    form.zip_code.data = venue.zip_code

    # Event Info
    form.title.data = event.title
    form.event_type.data = event.event_type.id
    form.category.data = event.event_category.id
    form.start_date.data = event.start_date()
    form.end_date.data = event.end_date()
    form.start_time.data = CreateEventForm.convert_choice_to_id(event.start_time(), "TIMES")
    form.end_time.data = CreateEventForm.convert_choice_to_id(event.end_time(), "TIMES")


def update_models_from_create_event_form(form, venue, event):
    """Helper function to update Venue and Event models with data
    from the Create Event form.
    """

    # Venue Info
    event.venue.name = form.venue_name.data
    event.venue.address = form.address.data
    event.venue.city = form.city.data
    event.venue.state = CreateEventForm.convert_choice_to_value(form.state.data, "STATES")
    event.venue.zip_code = form.zip_code.data

    # Event info
    event.title = form.title.data
    event_type = EventType.query.get(form.event_type.data)
    event_category = EventCategory.query.get(form.category.data)
    start_time = CreateEventForm.convert_choice_to_value(form.start_time.data, "TIMES")
    end_time = CreateEventForm.convert_choice_to_value(form.end_time.data, "TIMES")
    event.start_datetime = datetime.combine(form.start_date.data, start_time)
    event.end_datetime = datetime.combine(form.end_date.data, end_time)