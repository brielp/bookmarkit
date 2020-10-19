from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Regexp, Optional
from wtforms.fields.html5 import DateField


class SignupForm(FlaskForm):
    """ Form to sign up a user """

    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])

class LoginForm(FlaskForm):
    """ Form for Existing Users to Log in """

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[Length(min=6)])

class AddBoardForm(FlaskForm):
    """ Add a new Board """

    title = StringField("Board Title", validators=[DataRequired()])
    description = StringField("Description", validators=[DataRequired()])

class AddPostForm(FlaskForm):
    """ Add new post based off URL """

    url = StringField('URL', validators=[
        DataRequired('URL is required'),
        Regexp('^(http|https):\/\/[\w.\-]+(\.[\w.\-]+)+.*$', 0,
               'URL must be a valid link')])
    complete_by = DateField("Date Due", validators=[Optional()])