from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError


class LoginForm(FlaskForm):
    password = PasswordField("PGDx Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class GoForm(FlaskForm):
    process_latest = SubmitField("Process Latest Batch")


class SetupForm(FlaskForm):
    batch = StringField("Batch")
    submit_batch = SubmitField("Process")


class ConfirmForm(FlaskForm):
    yes = SubmitField("Yes")


class FinalForm(FlaskForm):
    yes = SubmitField("Start Processing")
