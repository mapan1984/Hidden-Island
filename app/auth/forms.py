from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError

from app.models import User


class LoginForm(FlaskForm):
    email = StringField('邮件地址', validators=[Required(), Length(1, 64),
                                                Email()])
    password = PasswordField('密码', validators=[Required()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    email = StringField('邮件', validators=[Required(), Length(1, 64),
                                            Email()])
    username = StringField('用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          '用户名只允许包含字符、数字、'
                                          '小数点与下划线')])
    password = PasswordField('密码', validators=[
        Required(), EqualTo('password2', message='密码必须相同')])
    password2 = PasswordField('重复密码', validators=[Required()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮件地址已经被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经被使用')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[Required()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='密码必须相同')])
    password2 = PasswordField('重复新密码', validators=[Required()])
    submit = SubmitField('更改密码')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('邮件地址', validators=[Required(), Length(1, 64),
                                                Email()])
    submit = SubmitField('重置密码')


class PasswordResetForm(FlaskForm):
    email = StringField('邮件地址', validators=[Required(), Length(1, 64),
                                                Email()])
    password = PasswordField('新密码', validators=[
        Required(), EqualTo('password2', message='密码必须相同')])
    password2 = PasswordField('重复密码', validators=[Required()])
    submit = SubmitField('重置密码')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('未知邮件地址')


class ChangeEmailForm(FlaskForm):
    password = PasswordField('密码', validators=[Required()])
    email = StringField('新邮件地址', validators=[Required(), Length(1, 64),
                                                  Email()])
    submit = SubmitField('更改邮件地址')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮件地址已经被注册')
