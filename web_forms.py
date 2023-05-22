from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, FileField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField

# Create a Search From
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create Login
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create Postform
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    #content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField('Content', validators=[DataRequired()])
    author = StringField("Author")
    slug =StringField("Slug")
    submit = SubmitField("Submit")

# Create a From Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favourite_color = StringField("Favourite Color")
    about_author = TextAreaField("About Author")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    profile_pic = FileField("Profile Pic")
    submit = SubmitField("Submit")

# Create a From Class
class NamerForm(FlaskForm):
    name = StringField("Whats your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

# PasswordForm
class PasswordForm(FlaskForm):
    email = StringField("Whats your Email", validators=[DataRequired()])
    password_hash = PasswordField("Whats your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")
