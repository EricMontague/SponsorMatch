from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    SubmitField,
    StringField,
    PasswordField,
    ValidationError,
    RadioField,
    TextAreaField,
)
from wtforms.fields.html5 import URLField
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    Regexp,
    EqualTo,
    URL,
    Optional,
)
from ..models import User


class ChangePasswordForm(FlaskForm):
    """Class to represent a form to let a user change their password"""

    old_password = PasswordField("Old Password", validators=[DataRequired()])
    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            EqualTo("confirm_password", message="Passwords must match."),
        ],
    )
    confirm_password = PasswordField("Confirm password", validators=[DataRequired()],)
    submit = SubmitField("Change Password")


class ChangeEmailForm(FlaskForm):
    """Class to represent a form that lets a user change their email"""

    email = StringField(
        "New email address", validators=[DataRequired(), Email(), Length(1, 64)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Change Email")

    def validate_email(self, field):
        """Custom validator to checl if the new email already belongs to another user"""
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("Email already registered.")


class CloseAccountForm(FlaskForm):
    """Class to represent a form to let a user close their account"""

    confirm = StringField('Type "CLOSE"', validators=[DataRequired()])
    submit = SubmitField("Close your account")

    def validate_confirm(self, field):
        """Custom validator for the confirm field"""
        if not field.data == "CLOSE":
            raise ValidationError('Please enter "CLOSE".')
