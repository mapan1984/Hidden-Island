from flask import render_template, current_app, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app.auth import auth
from app.auth.forms import (LoginForm, RegistrationForm, ChangePasswordForm,
                            PasswordResetRequestForm, PasswordResetForm,
                            ChangeEmailForm)
from app.models import User, Role
from app.email import send_email


@auth.before_app_request
def before_request():
    """
    更新用户的最后访问时间
    重定向未确认的用户到/auth/unconfirmed页面
    """
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash("无效的邮件地址")
        elif not user.verify_password(form.password.data):
            flash("无效的密码")
        else:
            current_app.logger.info('User login: %s\n' % user.email)
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("你已经退出登录")
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                    role=Role.query.filter_by(name='User').first())
        db.session.add(user)
        db.session.commit()  # 提交数据库后才可赋予新用户id值，不能延后提交
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('一封确认邮件已经发送到您的邮箱')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def confirm_request():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('一封确认邮件已经发送到您的邮箱')
    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('你已经确认了您的账户，谢谢!')
    else:
        flash('确认链接无效或过期')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('您的密码已经更新')
            return redirect(url_for('main.index'))
        else:
            flash('无效的密码')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_password_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('已发送一封包含重置密码说明的电子邮件到您的邮箱')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('您的密码已被更新')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_change_email_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('已发送一封包含确认您新邮件地址说明的电子邮件到您的邮箱')
            return redirect(url_for('main.index'))
        else:
            flash('无效的邮件地址或密码')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('您的邮件地址已被更新')
    else:
        flash('无效的请求')
    return redirect(url_for('main.index'))
