"""This module contains forms for the events blueprint."""


from app.models import EventCategory, EventType
from datetime import datetime, date
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields.html5 import DateField, URLField
from wtforms.validators import DataRequired, Length, URL, NumberRange, Email
from app.forms import STATES, PACKAGE_TYPES, PEOPLE_RANGES, TIMES, AbstractForm
from wtforms import (
    SubmitField,
    StringField,
    SelectField,
    TextAreaField,
    ValidationError,
    DecimalField,
    IntegerField,
    MultipleFileField,
)


class CreateEventForm(AbstractForm):
    """Class to represent a form to allow a user to enter basic event information
    when creating an event.
    """

    title = StringField("Event Title", validators=[DataRequired(), Length(1, 64)])
    event_type = SelectField("Type", coerce=int)
    category = SelectField("Category", coerce=int)
    venue_name = StringField("Venue Name", validators=[DataRequired(), Length(1, 64)])
    address = StringField("Address", validators=[DataRequired(), Length(1, 64)])
    city = StringField("City", validators=[DataRequired(), Length(1, 64)])
    state = SelectField("State", choices=[(0, "Select State...")] + STATES, coerce=int)
    zip_code = StringField("ZIP Code", validators=[DataRequired(), Length(5, 10)])
    start_date = DateField("Start date", default=date.today(), validators=[DataRequired()])
    end_date = DateField("End date", default=date.today(), validators=[DataRequired()])
    start_time = SelectField("Start time", choices=TIMES, coerce=int)
    end_time = SelectField("End time", choices=TIMES, coerce=int)
    submit = SubmitField("Save & Continue")

    def __init__(self, **kwargs):
        super(CreateEventForm, self).__init__(**kwargs)
        self.event_type.choices = [(0, "Select Event Type...")] + [
            (event_type.id, event_type.name)
            for event_type in EventType.query.order_by(EventType.name).all()
        ]
        self.category.choices = [(0, "Select Category...")] + [
            (category.id, category.name)
            for category in EventCategory.query.order_by(EventCategory.name).all()
        ]

    def validate_event_type(self, field):
        """Custom validation for the event_type field."""
        if field.data == 0:
            raise ValidationError("Please select an event type.")

    def validate_state(self, field):
        """Custom validation for the state field."""
        if field.data == 0:
            raise ValidationError("Please select a state.")

    def validate_category(self, field):
        """Custom validation for the category field."""
        if field.data == 0:
            raise ValidationError("Please select an event category.")

    def validate_start_date(self, field):
        """Custom validator to ensure that the start date field
        can't be set to a date before the current date
        """
        # field.data should be a datetime object
        if field.data < date.today():
            raise ValidationError("Start date can't be a date in the past.")

    def validate_end_date(self, field):
        """Custom validation method to ensure that the end date cannot be
        before the start date
        """
        # field.data should be a datetime object
        if field.data < self.start_date.data:
            raise ValidationError("End date must be on or after start date.")

    def validate_start_time(self, field):
        """Custom validation method to ensure that if the event starts on
        the current day, that the start time field can't be set to a time earlier 
        than the current time.
        """
        # convert string time to a time object
        start_time = CreateEventForm.convert_choice_to_value(field.data, "TIMES")
        start_datetime = datetime.combine(self.start_date.data, start_time)
        # check if user's event is today and if time is before the current time
        if (
            start_datetime.date() == datetime.today().date()
            and start_datetime < datetime.now()
        ):
            raise ValidationError("Start time can't be in the past.")

    def validate_end_time(self, field):
        """Custom validation method to ensure that the end time cannot be
        before the start time.
        """
        # convert string time to a time object
        start_time = CreateEventForm.convert_choice_to_value(
            self.start_time.data, "TIMES"
        )
        # datetime object
        end_time = CreateEventForm.convert_choice_to_value(field.data, "TIMES")
        if end_time <= start_time:
            if self.start_date.data == self.end_date.data:
                raise ValidationError("End time must be after start time.")


class EventDetailsForm(AbstractForm):
    """Form to allow the user to enter event details in a longer format"""

    description = TextAreaField(
        "Event Description", validators=[DataRequired()], render_kw={"rows": 6}
    )
    pitch = TextAreaField(
        "Your sponsorship pitch", validators=[DataRequired()], render_kw={"rows": 6}
    )
    submit = SubmitField("Save & Continue")


class EventPackagesForm(AbstractForm):
    """Form to allow the user to select sponsorship packages for their event."""

    name = StringField("Name", validators=[DataRequired(), Length(1, 64)])
    price = DecimalField("Price", validators=[NumberRange(min=1, max=2147483647)])
    audience = SelectField("Audience Reached", coerce=int, choices=PEOPLE_RANGES)
    description = TextAreaField(
        "Description", validators=[DataRequired()], render_kw={"rows": 5},
    )
    available_packages = IntegerField(
        "Number of available packages", validators=[NumberRange(min=1, max=2147483647)]
    )
    package_type = SelectField("Type", coerce=int, choices=PACKAGE_TYPES)
    submit = SubmitField("Save")

    def validate_audience(self, field):
        """Custom validation for the audience field."""
        if field.data == 1:
            raise ValidationError("Please choose the audience reached.")


class UploadImageForm(AbstractForm):
    """Class to represent a form to let a user upload an image."""

    image = FileField(
        "Upload image",
        validators=[
            FileRequired("Please upload an image."),
            FileAllowed(["png", "jpg", "jpeg"], "File type not allowed."),
        ],
    )
    upload = SubmitField("Upload")


class RemoveImageForm(AbstractForm):
    """Class to represent a form to let a user remove an image."""

    submit = SubmitField("Remove")


class UploadVideoForm(AbstractForm):
    """Class to represent a form that allows the user to upload the urls
    for videos."""

    video_url = URLField(
        "Add Video",
        validators=[DataRequired(), URL(message="Please provide a valid url.")],
        render_kw={"placeholder": "http://www.youtube.com/"},
    )
    add = SubmitField("Upload")

    @staticmethod
    def parse_url(url):
        """Parse the YouTube video url and reformat it so that it can be
        embedded in the page.
        """
        domain = "https://www.youtube.com/embed/"
        url_parts = url.split("/")
        video_id = url_parts[-1][8:]
        if url_parts[3] == "embed":
            return url
        return domain + video_id


class RemoveVideoForm(AbstractForm):
    """Class to represent a form to allow a user to delete a video
    they've uploaded to their event.
    """

    remove = SubmitField("Remove")


class MultipleImageForm(AbstractForm):
    """Class to represent a form that allows the user to upload multiple
    images to their event.
    """

    images = MultipleFileField(
        "Upload Image(s)", validators=[DataRequired("Please upload at least one image")]
    )
    upload = SubmitField("Upload")

    def validate_images(self, field):
        """Custom validation for the images field."""
        # FileRequired class not working for MultipleFileField
        allowed = ["png", "jpg", "jpeg"]
        for data in field.data:
            if data.filename.split(".")[-1] not in allowed:
                raise ValidationError("File type not allowed.")


class DemographicsForm(AbstractForm):
    """Class to represent a form that allows the user to enter details
    about who is expected to attend the event.
    """

    attendees = SelectField("Attendees", coerce=int, choices=PEOPLE_RANGES)
    males = IntegerField(
        "Percentage of males", validators=[NumberRange(min=0, max=100)]
    )
    females = IntegerField(
        "Percentage of females", validators=[NumberRange(min=0, max=100)]
    )
    submit = SubmitField("Submit")

    def validate_attendees(self, field):
        """Custom validation for the attendees field."""
        if field.data == 1:
            raise ValidationError("Please choose the number of attendees.")

    def validate_males(self, field):
        """Custom validation to validate that the sum of the percentages
        of males and females equals 100.
        """
        if field.data + self.females.data != 100:
            raise ValidationError("Sum of males and females must equal 100.")
        


class ContactForm(AbstractForm):
    """Class to represent a contact form for organizers."""

    name = StringField("Your Name", validators=[DataRequired(), Length(1, 64)])
    email = StringField(
        "Email Address", validators=[DataRequired(), Length(1, 64), Email()]
    )
    subject = StringField("Subject", validators=[DataRequired(), Length(1, 64)])
    message = TextAreaField(
        "Message", validators=[DataRequired()], render_kw={"rows": 6},
    )
    submit = SubmitField("Send")
