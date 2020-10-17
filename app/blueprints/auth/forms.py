"""This module contains forms for the auth blueprint."""


from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    StringField,
    PasswordField,
    BooleanField,
    ValidationError,
    SelectField,
)
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from app.models import User, Role


class LoginForm(FlaskForm):
    """Class to represent a login form"""

    email = StringField(
        "Email",
        validators=[DataRequired(), Length(1, 64), Email()],
        render_kw={"placeholder": "Email"},
    )
    password = PasswordField(
        "Password", validators=[DataRequired()], render_kw={"placeholder": "Password"}
    )
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    """Class to represent a registration form"""

    first_name = StringField(
        "First Name",
        validators=[DataRequired(), Length(1, 64)],
        render_kw={"placeholder": "First Name"},
    )
    last_name = StringField(
        "Last Name",
        validators=[DataRequired(), Length(1, 64)],
        render_kw={"placeholder": "Last Name"},
    )
    company = StringField(
        "Company",
        validators=[DataRequired(), Length(1, 64)],
        render_kw={"placeholder": "Company"},
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Length(1, 64), Email()],
        render_kw={"placeholder": "Email"},
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired()
        ],
        render_kw={"placeholder": "Password"},
    )
    role = SelectField("Choose account", coerce=int)
    submit = SubmitField("Create Account")

    def __init__(self, **kwargs):
        super(RegistrationForm, self).__init__(**kwargs)
        self.role.choices = [(0, "Choose account type...")] + [
            (role.id, role.name)
            for role in Role.query.filter(Role.name != "Administrator")
            .order_by(Role.name)
            .all()
        ]

    def validate_company(self, field):
        """Custom form validator for company field"""
        if User.query.filter_by(company=field.data).first():
            raise ValidationError("Company already registered.")

    def validate_email(self, field):
        """Custom form validator for email field"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email already registered.")

    def validate_role(self, field):
        """Custom form validator for the role field."""
        if field.data == 0:
            raise ValidationError("Please select an account type.")


class PasswordResetRequestForm(FlaskForm):
    """Class to represent a request to reset a user password"""

    email = StringField(
        "Email",
        validators=[DataRequired(), Length(1, 64), Email()],
        render_kw={"placeholder": "Email"},
    )
    submit = SubmitField("Submit")


class PasswordResetForm(FlaskForm):
    """Class to represent a form to allow a user to reset their password"""

    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            EqualTo("confirm_password", message="Passwords must match."),
        ],
        render_kw={"placeholder": "Password"},
    )
    confirm_password = PasswordField(
        "Confirm new password",
        validators=[DataRequired()],
        render_kw={"placeholder": "Confirm Password"},
    )
    submit = SubmitField("Reset Password")
