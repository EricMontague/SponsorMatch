"""This module contains forms classes for the users blueprint."""


from wtforms.validators import DataRequired, Length, Optional, URL, Email
from wtforms.fields.html5 import URLField
from app.models import User, Role
from app.forms import AbstractForm
from wtforms import (
    SubmitField,
    StringField,
    SelectField,
    TextAreaField,
    ValidationError,
    BooleanField
)


class EditProfileForm(AbstractForm):
    """Class to represent a form to let a user edit their profile information"""

    first_name = StringField("First Name", validators=[DataRequired(), Length(1, 64)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(1, 64)])
    company = StringField(
        "Company/Organization", validators=[DataRequired(), Length(1, 64)]
    )
    about = TextAreaField(
        "About the Organizer",
        render_kw={
            "class": "form-control",
            "rows": 6,
            "placeholder": "Tell us about your organization",
        },
    )
    job_title = StringField("Job title", validators=[Length(0, 64)])
    website = URLField(
        "Website",
        validators=[URL(message="Please provide a valid url."), Optional()],
        default=None,
        render_kw={"placeholder": "http://www.example.com"}
    )
    submit = SubmitField("Save")

    def __init__(self, user, **kwargs):
        super(EditProfileForm, self).__init__(**kwargs)
        self.user = user

    def validate_company(self, field):
        """Custom validation for the company field to ensure that a duplicate
        company name can't be added.
        """
        if (
            self.company.data != self.user.company
            and User.query.filter_by(company=self.company.data).first()
        ):
            raise ValidationError("Company already registered.")

    def validate_website(self, field):
        """Custom validation for the website field
        to ensure that a duplicate company website url can't be added.
        """
        if (
            self.website.data != self.user.website
            and User.query.filter_by(website=self.website.data).first()
        ):
            raise ValidationError("Company website already registerd.")
        

class EditProfileAdminForm(AbstractForm):
    """Class to represent a form that allows the admin to edit a user's
    profile information."""

    email = StringField("Email", validators=[DataRequired(), Length(1, 64), Email()])
    role = SelectField("Role", coerce=int)
    has_paid = BooleanField("User has Paid")
    submit = SubmitField("Save")

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(user, *args, **kwargs)
        self.role.choices = [
            (role.id, role.name) for role in Role.query.order_by(Role.name).all()
        ]
        self.user = user

    def validate_email(self, field):
        """Custom validation for the email field."""
        if (
            field.data != self.user.email
            and User.query.filter_by(email=field.data).first()
        ):
            raise ValidationError("Email already registered")
