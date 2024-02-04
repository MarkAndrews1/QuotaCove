from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, EmailField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length

class SignUpForm(FlaskForm):
    """Form for signing up"""

    username = StringField('Username', validators=[DataRequired(), Length(max=30)])
    email = EmailField('E-mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)], id='password')
    show_password = BooleanField('Show Password', id='check')
    fav_quote = StringField('(Optional) Favorite Quote')
    fav_quote_author = StringField('(Optional) Favorite Quote Author')
    img_url = StringField('(Optional) Profile Image URL')


class LoginForm(FlaskForm):
    """Form for loging in a user"""

    username = StringField('Username', validators=[DataRequired(), Length(max=30)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)], id='password')
    show_password = BooleanField('Show Password', id='check')

class QuoteForm(FlaskForm):
    """Form for adding quotes"""

    text = StringField('Write your quote...', validators=[DataRequired(), Length(max=1000)])
    author = StringField('Author', validators=[DataRequired()])

class EditUserForm(FlaskForm):
    """Form for editing a user"""

    username = StringField('Username', validators=[DataRequired(), Length(max=30)])
    email = EmailField('E-mail', validators=[DataRequired()])
    fav_quote = StringField('(Optional) Favorite Quote')
    fav_quote_author = StringField('(Optional) Favorite Quote Author')
    img_url = StringField('(Optional) Profile Image URL')
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)], id='password')
    show_password = BooleanField('Show Password', id='check')
