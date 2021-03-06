from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Required, Length
from flask_pagedown.fields import PageDownField

from app.models import Category, Article


class EditArticleForm(FlaskForm):
    title = StringField('题目', validators=[Required(), Length(1, 64)])
    category = SelectField('分类', coerce=int)
    tags = StringField('标签', validators=[Length(0, 64)])
    body = PageDownField("文章内容", validators=[Required()])
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(EditArticleForm, self).__init__(*args, **kwargs)
        self.category.choices = [
            (category.id, category.name)
            for category in Category.query.order_by(Category.name).all()
        ]

    def validate_title(self, field):
        if (Article.query.filter_by(name=field.data).first()
                or Article.query.filter_by(title=field.data).first()):
            raise ValidationError('文章标题已被使用')


class ModifyArticleForm(FlaskForm):
    title = StringField('题目', validators=[Required(), Length(1, 64)])
    category = SelectField('分类', coerce=int)
    tags = StringField('标签', validators=[Length(0, 64)])
    body = PageDownField("文章内容", validators=[Required()])
    submit = SubmitField('提交')

    def __init__(self, *args, **kwargs):
        super(ModifyArticleForm, self).__init__(*args, **kwargs)
        self.category.choices = [
            (category.id, category.name)
            for category in Category.query.order_by(Category.name).all()
        ]

