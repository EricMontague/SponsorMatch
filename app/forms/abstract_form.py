"""This module contains a class that subclass FlaskForm to extend
its functionality.
"""


from flask_wtf import FlaskForm


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