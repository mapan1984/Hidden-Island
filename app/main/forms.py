from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import Required, Length
from flask_pagedown.fields import PageDownField

from app.models import Category


class CommentForm(FlaskForm):
    body = StringField('', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditArticleForm(FlaskForm):
    title = StringField('Title', validators=[Required(), Length(1, 64)])
    category = SelectField('Category', coerce=int)
    tags = StringField('Tags', validators=[Length(0, 64)])
    body = PageDownField("What's on your mind?", validators=[Required()])
    submit = SubmitField('Submit')

    def __init__(self, article=None, *args, **kwargs):
        super(EditArticleForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
                 for category in Category.query.order_by(Category.name).all()]

