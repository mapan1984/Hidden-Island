from flask import render_template, current_app, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required

from app import db
from app.auth import auth
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User, Role
from app.email import send_email

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            current_app.logger.info('User login: %s\n' % user.email)
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash("Invalid email or password")
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
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
        send_email(current_app.config['ADMIN_EMAIL'], ' Refresh',
                   'mail/new_user', user=user)
        flash('You can now login.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
