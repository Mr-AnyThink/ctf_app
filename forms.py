# forms.py
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, EqualTo

class RegisterForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=150)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=200)]
    )
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=150)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")

class ChallengeForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Description", validators=[DataRequired()])
    category = StringField("Category", validators=[DataRequired(), Length(max=100)])
    hint = TextAreaField("Hint")
    answer_info = TextAreaField("More Information About the Answer")
    flag = StringField("Flag", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Create Challenge")

class SubmissionForm(FlaskForm):
    flag = StringField("Flag", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Submit Flag")

class ChangePasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('new_password', message="Passwords must match.")
    ])
    submit = SubmitField('Change Password')
