"""This module contains classes for the main blueprint."""


from flask import request
from datetime import date
from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    StringField,
    SelectField,
    ValidationError
)
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Optional, Email
from app.helpers import STATES, FormMixin
from app.models import EventCategory, EventType


class SearchForm(FlaskForm):
    """Class to represent a search bar."""

    query = StringField(
        "Search",
        validators=[DataRequired()],
        render_kw={"placeholder": "Find events"},
    )
    search = SubmitField("Search")

    def __init__(self, *args, **kwargs):
        # form data will be in the query string of the url
        if "formdata" not in kwargs:
            kwargs["formdata"] = request.args
        # need to disable for search to work
        if "csrf_enabled" not in kwargs:
            kwargs["csrf_enabled"] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class AdvancedSearchForm(FormMixin, FlaskForm):
    """Class to represent a search form that allows the user to
    perform mroe specific searches.
    """

    start_date = DateField("Start Date", default=date.today())
    end_date = DateField("End Date", default=date.today())
    city = StringField("City", validators=[Optional(), Length(1, 64)])
    state = SelectField("State", choices=[(0, "Select State...")] + STATES, coerce=int)
    category = SelectField("Categories", coerce=int)
    submit = SubmitField("Search")

    def __init__(self, **kwargs):
        super(AdvancedSearchForm, self).__init__(**kwargs)
        self.category.choices = [(0, "All")] + [
            (category.id, category.name)
            for category in EventCategory.query.order_by(EventCategory.name).all()
        ]

    def validate_state(self, field):
        """Custom validation for the state field."""
        if field.data == 0:
            raise ValidationError("Please select a state.")

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


