from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Required

class LoginForm(FlaskForm):
    name = StringField('name', validators=[Required()])
    password = PasswordField('password', validators=[Required()])
    submit = SubmitField('Submit')
