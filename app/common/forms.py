"""This module contains constants, classes and helper functions to
be used throughout the application.
"""


from datetime import datetime, timedelta
from flask_wtf import FlaskForm


TIME_FORMAT = "%I:%M %p"


STATES = [
    (1, "Alabama"),
    (2, "Alaska"),
    (3, "Arizona"),
    (4, "Arkansas"),
    (5, "California"),
    (6, "Colorado"),
    (7, "Connecticut"),
    (8, "District of Columbia"),
    (9, "Delaware"),
    (10, "Florida"),
    (11, "Georgia"),
    (12, "Hawaii"),
    (13, "Idaho"),
    (14, "Illinois"),
    (15, "Indiana"),
    (16, "Iowa"),
    (17, "Kansas"),
    (18, "Kentucky"),
    (19, "Louisiana"),
    (20, "Maine"),
    (21, "Maryland"),
    (22, "Massaachusetts"),
    (23, "Michigan"),
    (24, "Minnesota"),
    (25, "Mississippi"),
    (26, "Missouri"),
    (27, "Montana"),
    (28, "Nebraska"),
    (29, "Nevada"),
    (30, "New Hampshire"),
    (31, "New Jersey"),
    (32, "New Mexico"),
    (33, "New York"),
    (34, "North Carolina"),
    (35, "North Dakota"),
    (36, "Ohio"),
    (37, "Oklahoma"),
    (38, "Oregon"),
    (39, "Pennsylvania"),
    (40, "Rhode Island"),
    (41, "South Carolina"),
    (42, "South Dakota"),
    (43, "Tennessee"),
    (44, "Texas"),
    (45, "Utah"),
    (46, "Vermont"),
    (47, "Virginia"),
    (48, "Washington"),
    (49, "West Virginia"),
    (50, "Wisconsin"),
    (51, "Wyoming"),
]


PACKAGE_TYPES = [(1, "Cash"), (3, "In-Kind")]


PEOPLE_RANGES = [
    (1, "Choose range..."),
    (2, "1 - 50"),
    (3, "51 - 100"),
    (4, "101 - 250"),
    (5, "251 - 500"),
    (6, "501 - 1000"),
    (7, "1001 - 2500"),
    (8, "2501 - 5000"),
    (9, "5001 - 10000"),
    (10, "10000+"),
]


class AbstractForm(FlaskForm):
    """Abstract base class to extend the functionality of FlaskForm"""

    def populate_from_obj(self, obj):
        """Populate the form's field values based on the matching
        attributes in the given object.
        """
        for field in self:
            if hasattr(obj, field.name):
                value = getattr(obj, field.name)
                setattr(field, "data", value)

    @staticmethod
    def convert_choice_to_value(choice_id, choices):
        """Return the value selected from a SelectField form element."""
        choices = choices.upper()
        choice_list = globals().get(choices, None)
        if choice_list:
            choice_value = dict(choice_list).get(choice_id)
            if choices == "TIMES":
                return datetime.strptime(choice_value, TIME_FORMAT).time()
            return choice_value
        else:
            return None

    @staticmethod
    def convert_choice_to_id(choice_value, choices):
        """Return the id associated with given value in a SelectField
        form element.
        """
        choices = choices.upper()
        reversed_choices = {
            choice: choice_id for choice_id, choice in globals()[choices]
        }
        if reversed_choices:
            if choices == "TIMES":
                choice_value = choice_value.strftime(TIME_FORMAT)
            return reversed_choices[choice_value]
        else:
            return None


def time_intervals(start, end, delta):
    """Return a list of tuples containing an id and a datetime.time object
   with each datetime.time object separated by the given delta
   """
    times = []
    i = 1
    current = start
    while current <= end:
        times.append((i, current.strftime(TIME_FORMAT)))
        current += delta
        i += 1
    return times


# a list of a 30 minute time intervals as strings
TIMES = time_intervals(
    datetime(2019, 11, 19, 0), datetime(2019, 11, 19, 23, 30), timedelta(minutes=30)
)
