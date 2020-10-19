"""This module contains view functions for the events blueprint."""


import os
import uuid
from datetime import datetime
from flask_login import login_required, current_user
from app.blueprints.events import events
from sqlalchemy.exc import IntegrityError
from app.extensions import db, images
from app.helpers import send_email
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
from app.helpers import permission_required


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
            venue = Venue(
                name=form.venue_name.data,
                address=form.address.data,
                city=form.city.data,
                state=CreateEventForm.choice_value(form.state.data, "STATES"),
                zip_code=form.zip_code.data,
            )
        event_type = EventType.query.get(form.event_type.data)
        event_category = EventCategory.query.get(form.category.data)
        start_time = CreateEventForm.choice_value(form.start_time.data, "TIMES")
        end_time = CreateEventForm.choice_value(form.end_time.data, "TIMES")
        event = Event(
            title=form.title.data,
            start_datetime=datetime.combine(form.start_date.data, start_time),
            end_datetime=datetime.combine(form.end_date.data, end_time),
            venue=venue,
            event_type=event_type,
            event_category=event_category,
            user=current_user._get_current_object(),
        )
        db.session.add(event)
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
        event.title = form.title.data
        event_type = EventType.query.get(form.event_type.data)
        event_category = EventCategory.query.get(form.category.data)
        event.venue.name = form.venue_name.data
        event.venue.address = form.address.data
        event.venue.city = form.city.data
        event.venue.state = CreateEventForm.choice_value(form.state.data, "STATES")
        event.venue.zip_code = form.zip_code.data

        start_time = CreateEventForm.choice_value(form.start_time.data, "TIMES")
        end_time = CreateEventForm.choice_value(form.end_time.data, "TIMES")

        event.start_datetime = datetime.combine(form.start_date.data, start_time)
        event.end_datetime = datetime.combine(form.end_date.data, end_time)
        db.session.commit()
        flash("Your changes were saved.")
        return redirect(url_for("events.edit_basic_info", id=id))
    venue = event.venue
    form.title.data = event.title
    form.event_type.data = event.event_type.id
    form.category.data = event.event_category.id
    form.venue_name.data = venue.name
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = CreateEventForm.choice_id(venue.state, "STATES")
    form.zip_code.data = venue.zip_code
    form.start_date.data = event.start_date()
    form.end_date.data = event.end_date()
    form.start_time.data = CreateEventForm.choice_id(event.start_time(), "TIMES")
    form.end_time.data = CreateEventForm.choice_id(event.end_time(), "TIMES")
    return render_template("events/create_event.html", form=form, event=event)


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
    main_image_path = event.main_image

    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))

    if details_form.validate_on_submit():
        event.description = details_form.description.data
        event.pitch = details_form.pitch.data
        db.session.commit()
        flash("Update successful.")
        return redirect(url_for("events.event_details", id=event.id))
    # pre-fill fields
    details_form.description.data = event.description
    details_form.pitch.data = event.pitch
    return render_template(
        "events/event_details.html",
        details_form=details_form,
        upload_image_form=upload_image_form,
        remove_image_form=remove_image_form,
        main_image_path=main_image_path,
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
        filename = images.save(form.image.data)
        image_type = ImageType.query.filter_by(name="Main Event Image").first()
        image = Image(path=images.path(filename), image_type=image_type, event=event)
        db.session.add(image)
        db.session.commit()
        flash("Your image was successfully uploaded.")
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
    flash("Your event image was successfully deleted.")
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
        if form.males.data + form.females.data != 100:
            flash("Sum of males and females must equal 100.")
        else:
            event.attendees = DemographicsForm.choice_value(
                form.attendees.data, "PEOPLE_RANGES"
            )
            distribution = str(form.males.data) + "-" + str(form.females.data)
            event.male_to_female = distribution
            db.session.commit()
            flash("Your information has been successfilly uploaded.")
            return redirect(url_for("events.demographics", id=id))
    if event.attendees:
        form.attendees.data = DemographicsForm.choice_id(
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
    packages that will go along with thier event.
    """
    form = EventPackagesForm()
    event = Event.query.get_or_404(id)
    packages = event.packages.all()
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    if form.validate_on_submit():
        package = Package(
            name=form.name.data,
            price=form.price.data,
            audience=EventPackagesForm.choice_value(
                form.audience.data, "PEOPLE_RANGES"
            ),
            description=form.description.data,
            available_packages=form.available_packages.data,
            package_type=EventPackagesForm.choice_value(
                form.package_type.data, "PACKAGE_TYPES"
            ),
            event=event,
        )
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
        package.name = form.name.data
        package.price = form.price.data
        package.audience = EventPackagesForm.choice_value(
            form.audience.data, "PEOPLE_RANGES"
        )
        package.description = form.description.data
        package.available_packages = form.available_packages.data
        package.package_type = EventPackagesForm.choice_value(
            form.package_type.data, "PACKAGE_TYPES"
        )
        db.session.commit()
        flash("Package details were successfully updated.")
        return redirect(url_for("events.packages", id=event_id))
    packages = event.packages.all()
    form.name.data = package.name
    form.price.data = package.price
    form.audience.data = EventPackagesForm.choice_id(package.audience, "PEOPLE_RANGES")
    form.description.data = package.description
    form.available_packages.data = package.available_packages
    form.package_type.data = EventPackagesForm.choice_id(
        package.package_type, "PACKAGE_TYPES"
    )
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
    db.session.delete(package)
    db.session.commit()
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
        flash("Your upload was successful.")
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
        image_type = ImageType.query.filter_by(name="Misc").first()
        for data in image_form.images.data:
            filename = images.save(data)
            image = Image(
                path=images.path(filename), image_type=image_type, event=event
            )
            db.session.add(image)
        db.session.commit()
        flash("Your upload was successful.")
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
    upload_video_form = UploadVideoForm()
    upload_video_form.video_url.errors = session.pop("upload_video_form_errors", [])
    upload_video_form.video_url.data = session.pop("video_url", "")
    remove_video_form = RemoveVideoForm()
    image_form = MultipleImageForm()
    image_form.images.errors = session.pop("image_form_errors", [])
    remove_image_form = RemoveImageForm()
    event = Event.query.get_or_404(id)
    video = event.video
    misc_image_paths = event.misc_images
    if not current_user.is_organizer(event) and not current_user.is_administrator():
        return redirect(url_for("main.index"))
    return render_template(
        "events/media.html",
        upload_video_form=upload_video_form,
        remove_video_form=remove_video_form,
        image_form=image_form,
        remove_image_form=remove_image_form,
        video=video,
        misc_image_paths=misc_image_paths,
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
    flash("Your video has been deleted.")
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
        flash("You cannot publish an event without adding a description or pitch.")
        return redirect(url_for("events.event_details", id=event.id))
    if event.packages.count() == 0:
        flash("You cannot publish an event without adding any packages.")
        return redirect(url_for("events.packages", id=event.id))
    event.published = True
    db.session.commit()
    flash("Your event has been published.")
    return redirect(url_for("main.index"))


@events.route("/<int:id>", methods=["GET", "POST"])
def event(id):
    """Return the view that displays the event's information"""
    other_media = {}
    date_format = "%m/%d/%Y"
    time_format = "%I:%M %p"
    form = ContactForm()
    event = Event.query.get_or_404(id)
    venue = event.venue
    organizer = event.user
    image_path = event.main_image
    other_media["video"] = event.video
    other_media["misc_image_paths"] = event.misc_images
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
        flash("Your email was sent to the event organizer.")
        return redirect(url_for("events.event", id=id))
    return render_template(
        "events/event.html",
        event=event,
        venue=venue,
        organizer=organizer,
        packages=packages,
        form=form,
        date_format=date_format,
        image_path=image_path,
        time_format=time_format,
        other_media=other_media,
    )


@events.route("/<int:id>/<tab>")
def event_tab(id, tab):
    """Return an html template with the appropriate content
    based on the tab clicked by the user on an event's page.
    """
    other_media = {}
    event = Event.query.get_or_404(id)
    image_path = event.main_image
    other_media["video"] = event.video
    other_media["misc_image_paths"] = event.misc_images
    if tab == "info":
        return render_template(
            "utils/_event_page_content.html",
            event=event,
            image_path=image_path,
            other_media=other_media,
        )
    elif tab == "sponsors":
        users = set()
        for sponsorship in event.sponsorships:
            if not sponsorship.is_pending():
                users.add(sponsorship.sponsor)
        return render_template("utils/_users.html", event=event, users=users)
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
    events = current_user.saved_events.all()
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


@events.route("/<int:id>/sponsorships", methods=["POST"])
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def create_sponsorships(id):
    """Create sponsorship objects and add them to the database."""
    event = Event.query.get_or_404(id)
    user = current_user._get_current_object()
    if not request.json or "ids" not in request.json:
        abort(400)
    for package_id in request.json["ids"]:
        package = Package.query.get_or_404(package_id)
        # user can't buy the same package twice
        try:
            sponsorship = Sponsorship(event=event, sponsor=user, package=package)
        except IntegrityError as err:  # need to test this
            return jsonify({"message": err, "url": url_for("events.event", id=event.id)})
        db.session.add(sponsorship)
    db.session.commit()
    return jsonify({"url": url_for("events.purchase", id=event.id)})


@events.route("/<int:id>/charge/<int:amount>", methods=["POST"])
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def charge(id, amount):
    """View function to handle the POST request sent when a
    user makes a payment.
    """
    event = Event.query.get_or_404(id)
    user = current_user._get_current_object()
    # sponsorship deals for this event that haven't been completed yet
    sponsorships = Sponsorship.query.filter(
        Sponsorship.confirmation_code.is_(None),
        Sponsorship.sponsor_id == user.id,
        Sponsorship.event_id == event.id,
    ).all()
    if sponsorships == []:  # user has no pending deals for this event
        return redirect(url_for("main.index"))
    try:
        customer = current_app.stripe.Customer.create(
            email=request.form["stripeEmail"], source=request.form["stripeToken"]
        )
        charge = current_app.stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency="usd",
            description="Sponsorship Deal",
        )
        confirmation_code = str(uuid.uuid4())
        for sponsorship in sponsorships:
            sponsorship.confirmation_code = confirmation_code
            sponsorship.timestamp = datetime.now()
            sponsorship.package.num_purchased += 1
            if (
                sponsorship.package.available_packages
                - sponsorship.package.num_purchased
                < 0
            ):  # out of stock
                db.session.rollback()
                flash("The package you attempted to purchase is sold out.")
                return redirect(url_for("events.event", id=event.id))
        db.session.commit()
        send_email(
            customer.email,
            "Your Recent Purchase",
            "events/email/purchase",
            user=user,
            sponsorships=sponsorships,
            amount=amount,
        )
        flash("Your purchase was successful. A confirmation email was sent to you.")
        return redirect(url_for("manage.manage_sponsorships", status="all"))
    # refactor needed. Maybe I can make a decorator to handle stripe errors?
    except current_app.stripe.error.CardError as err:
        # Since it's a decline, stripe.error.CardError will be caught
        db.session.rollback()
        flash("There was an error with your card, please try again.")
        return redirect(url_for("events.event", id=event.id))
    except current_app.stripe.error.RateLimitError as err:
        # Too many requests made to the API too quickly
        db.session.rollback()
        flash(
            "Sorry, we are experiencing high traffic volumes. Please wait 30 seconds before retrying your purchase."
        )
        return redirect(url_for("events.event", id=event.id))
    except current_app.stripe.error.InvalidRequestError as err:
        # Invalid parameters were supplied to Stripe's API
        db.session.rollback()
        flash("Invalid parameters were supplied, please try again.")
        return redirect(url_for("events.event", id=event.id))
    except current_app.stripe.error.AuthenticationError as err:
        # Authentication with Stripe's API failed
        db.session.rollback()
        flash(
            "We are having issues connecting to the Stripe API. We will try to resolve this issue as soon as possible. Please try to make your purchase again later."
        )
        return redirect(url_for("events.event", id=event.id))
    except current_app.stripe.error.APIConnectionError as err:
        # Network communication with Stripe failed
        db.session.rollback()
        flash(
            "We are having issues connecting to the Stripe API. We will try to resolve this issue as soon as possible. Please try to make your purchase again later."
        )
        return redirect(url_for("events.event", id=event.id))
    except current_app.stripe.error.StripeError as err:
        # Generic Stripe error
        db.session.rollback()
        flash(
            "We are having issues accessing the Stripe API. We will try to resolve this issue as soon as possible. Please try to make your purchase again later."
        )
        return redirect(url_for("events.event", id=event.id))
    except Exception as err:
        # Something else happened, completely unrelated to Stripe
        db.session.rollback()
        abort(500)


# need to lock the table to avoid a race condition
# then I need to decrement the quantity of available packages by 1 for
# each package that was purchased
@events.route("/<int:id>/sponsorships/purchase", methods=["GET", "POST"])
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def purchase(id):
    """Return a page that allows the sponsor to complete their
    purchases of the package(s).
    """
    form = ContactForm()
    event = Event.query.get_or_404(id)
    user = current_user._get_current_object()
    endpoint = "events.purchase"
    publishable_key = current_app.config["STRIPE_PUBLISHABLE_KEY"]
    
    # sponsorship deals for this event that haven't been completed yet
    amount = 0
    sponsorships = []
    for sponsorship in user.sponsorships:
        if sponsorship.event_id == event.id and sponsorship.is_pending():
            sponsorships.append(sponsorship)
            amount += sponsorship.package.price * 100
    url = url_for("events.charge", id=event.id, amount=amount)
    if sponsorships == []:  # user has no pending deals for this event
        return redirect(url_for("main.index"))
    flash(
        "Please note: Navigating away from or refreshing this page will cancel your purchase."
    )
    return render_template(
        "events/purchase.html",
        form=form,
        event=event,
        sponsorships=sponsorships,
        endpoint=endpoint,
        publishable_key=publishable_key,
        amount=amount,
        url=url,
    )


@events.route("/<int:id>/sponsorships/cancel-purchase", methods=["POST"])
@login_required
@permission_required(Permission.SPONSOR_EVENT)
def cancel_purchase(id):
    """Function to be activated when a user navigates away from
    the purchase page before completing their purchase. Delete
    the appropriate sponsorship objects from the database.
    """
    event = Event.query.get_or_404(id)
    user = current_user._get_current_object()
    sponsorships = [
        sponsorship
        for sponsorship in user.sponsorships
        if sponsorship.event_id == event.id and sponsorship.is_pending()
    ]
    if sponsorships != []:
        for sponsorship in sponsorships:
            try:
                db.session.delete(sponsorship)
            except exc.IntegrityError as err:
                db.session.rollback()
                abort(500)
        db.session.commit()
    return redirect(url_for("manage.manage_sponsorships", status="all"))
    


