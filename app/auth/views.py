from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required

from app.auth import auth 
from app.models import User
from app.auth.forms import LoginForm

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash("You have login")
            return redirect(url_for('admin.index'))
        else:
            flash("Login fail")
            return redirect(url_for('main.index'))
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have logout")
    return redirect(url_for('main.index'))
