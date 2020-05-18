from flask_wtf import Form
from wtforms import PasswordField, TextField
from wtforms.validators import DataRequired


class LoginForm(Form):
    email = TextField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
