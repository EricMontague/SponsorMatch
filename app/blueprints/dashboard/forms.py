"""This module contains form classes for the manage blueprint."""


from flask_wtf import FlaskForm
from wtforms import SelectField


class DropdownForm(FlaskForm):
    """Form to represent a dropdown menu of options."""

    filter = SelectField(
        choices=[(1, "All"), (2, "Live"), (3, "Past"), (4, "Draft")], coerce=int
    )

    def __init__(self, choices, **kwargs):
        super(DropdownForm, self).__init__(**kwargs)
        self.filter.choices = choices
