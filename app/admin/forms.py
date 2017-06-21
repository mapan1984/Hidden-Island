from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError

from app.models import Role, User


class EditProfileAdminForm(FlaskForm):
    email = StringField('邮件', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('用户名', validators=[
                                        Required(), Length(1, 64),
                                        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                               '用户名只允许包含字符、数字、'
                                               '小数点与下划线')])
    confirmed = BooleanField('确认')
    role = SelectField('角色', coerce=int)
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email \
                and User.query.filter_by(email=field.data).first():
            raise ValidationError('邮件已经被注册')

    def validate_username(self, field):
        if field.data != self.user.username \
                and User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被使用')

