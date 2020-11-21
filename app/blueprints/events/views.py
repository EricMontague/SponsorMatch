"""This module contains view functions for the events blueprint."""


import os
import uuid
from http import HTTPStatus
from datetime import datetime
from flask_login import login_required, current_user
from app.blueprints.events import events, services
from sqlalchemy.exc import IntegrityError
from app.extensions import db, images
from app.utils import send_email
from flask import (
    render_template,
    url_for,
    redirect,
    flash,
    request,
    abort,
    current_app,
    session,
    jsonify
)
from app.blueprints.events.forms import (
    CreateEventForm,
    EventDetailsForm,
    EventPackagesForm,
    UploadVideoForm,
    RemoveVideoForm,
    MultipleImageForm,
    DemographicsForm,
    UploadImageForm,
    RemoveImageForm,
    ContactForm
)
from app.models import (
    User,
    Image,
    ImageType,
    Event,
    EventType,
    EventCategory,
    Venue,
    Package,
    Video,
    Permission,
    Sponsorship
)
from app.utils import permission_required


@events.route("/create", methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def create_event():
    """Render the view that allows a user to create an event"""
    event = None
    form = CreateEventForm()
    if form.validate_on_submit():
        venue = Venue.query.filter_by(address=form.address.data).first()
        if venue is None:  # venue not already in db, need to add it
            venue_data = venue.__dict__
            venue_data["state"] = CreateEventForm.convert_choice_to_value(form.state.data, "STATES"),
            venue = Venue.create(**venue_data)
        event_type = EventType.query.get(form.event_type.data)
        event_category = EventCategory.query.get(form.category.data)
        start_time = CreateEventForm.convert_choice_to_value(form.start_time.data, "TIMES")
        end_time = CreateEventForm.convert_choice_to_value(form.end_time.data, "TIMES")
        event = Event(
            title=form.title.data,
            start_datetime=datetime.combine(form.start_date.data, start_time),
            end_datetime=datetime.combine(form.end_date.data, end_time),
            venue=venue,
            event_type=event_type,
            event_category=event_category,
            user=current_user._get_current_object(),
        )
        db.session.commit()
        return redirect(url_for("events.event_details", id=event.id))
    return render_template("events/create_event.html", form=form, event=event)


@events.route("/<int:id>/basic-info", methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def edit_basic_info(id):
    """Return the view that allows a user to edit an event's basic info."""
    form = CreateEventForm()
    form.submit.label.text = "Update Event"
    event = Event.query.get_or_404(id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    if form.validate_on_submit():
        services.update_models_from_create_event_form(form, event.venue, event)
        db.session.commit()
        flash("Your changes were saved.", "success")
        return redirect(url_for("events.edit_basic_info", id=id))
    services.populate_create_event_form(form, event.venue, event)
    return render_template("events/basic_info.html", form=form, event=event)


@events.route("/<int:id>/event-details", methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def event_details(id):
    """Render a page that allows the user to enter more details
    about the event.
    """
    details_form = EventDetailsForm()
    upload_image_form = UploadImageForm()
    remove_image_form = RemoveImageForm()
    details_form.submit.label.text = "Submit"
    event = Event.query.get_or_404(id)

    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))

    if details_form.validate_on_submit():
        event.description = details_form.description.data
        event.pitch = details_form.pitch.data
        db.session.commit()
        flash("Update successful.", "success")
        return redirect(url_for("events.event_details", id=event.id))
    # pre-fill fields
    details_form.description.data = event.description
    details_form.pitch.data = event.pitch
    return render_template(
        "events/event_details.html",
        details_form=details_form,
        upload_image_form=upload_image_form,
        remove_image_form=remove_image_form,
        main_image_path=event.main_image(),
        event=event,
    )


@events.route("/<int:id>/add-image", methods=["POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def add_event_image(id):
    """view function to add an image to the database."""
    form = UploadImageForm()
    event = Event.query.get_or_404(id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    if form.validate_on_submit():
        services.add_event_main_image(form.image.data, event, images, db.session)
        db.session.commit()
        flash("Your image was successfully uploaded.", "success")
        return redirect(url_for("events.event_details", id=id))
    return redirect(url_for("events.event_details", id=event.id))


@events.route("/images/<string:filename>/delete", methods=["POST"])
@login_required
def delete_image(filename):
    """View function to delete an event image."""
    referrer = request.referrer
    path = "/Users/ericmontague/sponsormatch/app/static/images/" + filename
    image = Image.query.filter_by(path=path).first_or_404()
    event = Event.query.get_or_404(image.event_id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    db.session.delete(image)
    db.session.commit()
    flash("Your event image was successfully deleted.", "success")
    return redirect(referrer)


@events.route("/<int:id>/demographics", methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def demographics(id):
    """Return a page that allows the user to give details
    about who is attending the event.
    """
    form = DemographicsForm()
    event = Event.query.get_or_404(id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    if form.validate_on_submit():
        event.attendees = DemographicsForm.convert_choice_to_value(
            form.attendees.data, "PEOPLE_RANGES"
        )
        event.male_to_female = str(form.males.data) + "-" + str(form.females.data)
        db.session.commit()
        flash("Your information has been successfilly uploaded.", "success")
        return redirect(url_for("events.demographics", id=id))
    if event.attendees:
        form.attendees.data = DemographicsForm.convert_choice_to_id(
            event.attendees, "PEOPLE_RANGES"
        )
    else:
        form.attendees.data = 1
    if event.male_to_female:
        distribution = event.male_to_female.split("-")
        form.males.data = distribution[0]
        form.females.data = distribution[1]
    else:
        form.males.data = 0
        form.females.data = 0
    return render_template("events/demographics.html", form=form, event=event)


@events.route("/packages/<int:id>")
@login_required
def view_package(id):
    """Return the details regarding a package as a json object."""
    package = Package.query.get_or_404(id)
    return jsonify(
        {
            "package_id": package.id,
            "event_id": package.event.id,
            "price": float(package.price),
            "audience": package.audience,
            "description": package.description,
            "package_type": package.package_type,
        }
    )


@events.route("/<int:id>/packages", methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def packages(id):
    """Render a page that allows the user to select the sponsorship
    packages that will go along with theri event.
    """
    form = EventPackagesForm()
    event = Event.query.get_or_404(id)
    packages = event.packages.all()
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    if form.validate_on_submit():
        form_data = form.data
        form_data["event"] = event
        form_data["audience"] = EventPackagesForm.convert_choice_to_value(
            form.audience.data, "PEOPLE_RANGES"
        )
        form_data["package_type"] = EventPackagesForm.convert_choice_to_value(
            form.package_type.data, "PACKAGE_TYPES"
        )
        package = Package.create(form_data)
        db.session.commit()
        return redirect(url_for("events.packages", id=id))
    return render_template(
        "events/packages.html", form=form, event=event, packages=packages
    )


@events.route(
    "/<int:event_id>/packages/<int:package_id>/edit", methods=["GET", "POST"]
)
@login_required
@permission_required(Permission.CREATE_EVENT)
def edit_package(event_id, package_id):
    """View function to add a package to an event in the database."""
    form = EventPackagesForm()
    event = Event.query.get_or_404(event_id)
    package = event.packages.filter(Package.id == package_id).first_or_404()
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    if form.validate_on_submit():
        form_data = form.data
        form_data["audience"] = EventPackagesForm.convert_choice_to_value(
            form.audience.data, "PEOPLE_RANGES"
        )
        form_data["package_type"] = EventPackagesForm.convert_choice_to_value(
            form.package_type.data, "PACKAGE_TYPES"
        )
        package.populate_from_form(form_data)
        db.session.commit()
        flash("Package details were successfully updated.", "success")
        return redirect(url_for("events.packages", id=event_id))
    packages = event.packages.all()
    package_data = package.__dict__
    package_data["audience" ] = EventPackagesForm.convert_choice_to_id(package.audience, "PEOPLE_RANGES")
    package_data["package_type"] = EventPackagesForm.convert_choice_to_id(
        package.package_type, "PACKAGE_TYPES"
    )
    form.populate_from_model(package_data)
    return render_template(
        "events/packages.html", form=form, event=event, packages=packages
    )


@events.route("/<int:event_id>/packages/<int:package_id>/delete", methods=["POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def delete_package(event_id, package_id):
    """View function to be executed when a user wants to remove
    a sponsorship package from their event.
    """
    event = Event.query.get_or_404(event_id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    
    package = event.packages.filter(Package.id == package_id).first_or_404()
    if package.was_purchased():
        flash("A package that was purchased cannot be deleted", "danger")
    else:
        db.session.delete(package)
        db.session.commit()
        flash(f"Package named {package.name} was successfully deleted", "success")        
    return jsonify({"url": url_for("events.packages", id=event.id)})


@events.route("/<int:id>/video", methods=["POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def add_video(id):
    """Add a video to the database for an event."""
    event = Event.query.get_or_404(id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    upload_video_form = UploadVideoForm()
    if upload_video_form.validate_on_submit():
        video = Video(
            url=UploadVideoForm.parse_url(upload_video_form.video_url.data), event=event
        )
        db.session.add(video)
        db.session.commit()
        flash("Your upload was successful.", "success")
        return redirect(url_for("events.media", id=id))
    else:
        session["upload_video_form_errors"] = upload_video_form.video_url.errors
        session["video_url"] = upload_video_form.video_url.data
    return redirect(url_for("events.media", id=event.id))


@events.route("/<int:id>/misc-images", methods=["POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def add_misc_images(id):
    """Add multiple images to the database for an event."""
    event = Event.query.get_or_404(id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    image_form = MultipleImageForm()
    if image_form.validate_on_submit():
        services.save_misc_images(image_form.images.data, event, images, db.session)
        db.session.commit()
        flash("Your upload was successful.", "success")
        return redirect(url_for("events.media", id=id))
    else:
        session["image_form_errors"] = image_form.images.errors
    return redirect(url_for("events.media", id=event.id))


@events.route("/<int:id>/media", methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def media(id):
    """Return a page that allows the user do at various forms of
    media to their event page."""
    event = Event.query.get_or_404(id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))

    # Instantiate forms
    upload_video_form = UploadVideoForm()
    remove_video_form = RemoveVideoForm()
    image_form = MultipleImageForm()
    remove_image_form = RemoveImageForm()

    # Get data from user session
    upload_video_form.video_url.errors = session.pop("upload_video_form_errors", [])
    upload_video_form.video_url.data = session.pop("video_url", "")
    image_form.images.errors = session.pop("image_form_errors", [])
    
    return render_template(
        "events/media.html",
        upload_video_form=upload_video_form,
        remove_video_form=remove_video_form,
        image_form=image_form,
        remove_image_form=remove_image_form,
        video=event.video,
        misc_image_paths=event.misc_images(),
        event=event,
    )


@events.route("/<int:event_id>/videos/<int:video_id>/delete", methods=["POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def delete_video(event_id, video_id):
    """View function to delete a video."""
    event = Event.query.get_or_404(event_id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    video = Video.query.get_or_404(video_id)
    db.session.delete(video)
    db.session.commit()
    flash("Your video has been deleted.", "success")
    return redirect(url_for("events.media", id=event_id))


@events.route("/<int:id>/publish", methods=["POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def publish(id):
    """View function that is called when a user wants to publish their
    event.
    """
    event = Event.query.get_or_404(id)
    if (
        not current_user.is_organizer(event) and not current_user.is_administrator()
    ) or event.has_ended():
        return redirect(url_for("main.index"))
    if event.description is None or event.pitch is None:
        flash("You cannot publish an event without adding a description or pitch.", "danger")
        return redirect(url_for("events.event_details", id=event.id))
    if event.packages.count() == 0:
        flash("You cannot publish an event without adding any packages.", "danger")
        return redirect(url_for("events.packages", id=event.id))
    event.published = True
    db.session.commit()
    flash("Your event has been published.", "success")
    return redirect(url_for("main.index"))


@events.route("/<int:id>", methods=["GET", "POST"])
def event(id):
    """Return the view that displays the event's information"""
    form = ContactForm()
    event = Event.query.get_or_404(id)
    other_media = {"video": event.video, "misc_image_paths": event.misc_images()}
    packages = event.packages.all()
    # commented out because the fake data generated for the demo of
    # this app by the Faker package may inadvertently contain real email addresses
    if form.validate_on_submit():
        # send_email(
        #     organizer.email,
        #     f"Event Inquiry - {form.subject.data}",
        #     "events/email/contact_organizer",
        #     organizer=organizer,
        #     form=form,
        #     event=event,
        # )
        flash("Your email was sent to the event organizer.", "success")
        return redirect(url_for("events.event", id=id))
    return render_template(
        "events/event.html",
        event=event,
        venue=event.venue,
        organizer=event.user,
        packages=packages,
        form=form,
        date_format="%m/%d/%Y",
        main_image=event.main_image(),
        time_format="%I:%M %p",
        other_media=other_media,
    )


@events.route("/<int:id>/<tab>")
def event_tab(id, tab):
    """Return an html template with the appropriate content
    based on the tab clicked by the user on an event's page.
    """
    event = Event.query.get_or_404(id)
    other_media = {"video": event.video, "misc_image_paths": event.misc_images()}
    if tab == "info":
        return render_template(
            "events/_event_page_content.html",
            event=event,
            image_path=event.main_image(),
            other_media=other_media,
        )
    elif tab == "sponsors":
        users = {sponsorship.sponsor for sponsorship in event.sponsorships}
        return render_template("users/_users.html", event=event, users=users)
    else:
        abort(404)


@events.route("/<int:id>/delete", methods=["POST"])
@login_required
@permission_required(Permission.CREATE_EVENT)
def delete_event(id):
    """View function to delete an event."""
    event = Event.query.get(id)
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    db.session.delete(event)
    db.session.commit()
    return jsonify({"message": "Your event has been successfully deleted."})


@events.route("/<int:id>/save", methods=["POST"])
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def save_event(id):
    """Route to allow a sponsor to save an event to their favorites list."""
    event = Event.query.get_or_404(id)
    if not current_user.has_saved(event):
        current_user.save(event)
        db.session.commit()
        return jsonify({"message": "Event added to your saved events list."})
    else:
        return jsonify({"message": "You have already saved this event."})


@events.route("/saved-events")
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def saved_events():
    """Return a page where sponsors can view their list of saved events."""
    endpoint = "events.saved_events"
    events = [
        (event.main_image(), event)
        for event in current_user.saved_events
    ]
    return render_template(
        "events/saved_events.html", events=events, endpoint=endpoint
    )


@events.route("/saved-events/<int:id>/delete", methods=["POST"])
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def delete_saved_event(id):
    """Remove the given saved event from the user's saved events list."""
    event = Event.query.get_or_404(id)
    if current_user.has_saved(event):
        current_user.unsave(event)
        db.session.commit()
        return jsonify(
            {"message": "The event was removed from your saved events list."}
        )
    return redirect(url_for("main.index"))


@events.route("/<int:id>/place-order", methods=["POST"])
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def place_order(id):
    """Create an order by storing the user's requested packages
    in a user session
    """
    data = services.validate_order(id, request.json, current_user)
    if "error" in data:
        return jsonify({"message": data["message"]}), HTTPStatus.BAD_REQUEST
    order_key = f"PENDING_ORDER#{current_user.id}#{data['event'].id}"
    session[order_key] = [
        {
            "package_id": package.id,
            "event_id": data["event"].id,
            "sponsor_id": current_user.id,
            "price": float(package.price),
            "name": package.name
        }
        for package in data["packages"]
    ]
    session["user"] = "Facebook"
    return jsonify({"url": url_for("payments.checkout", event_id=data["event"].id)})




