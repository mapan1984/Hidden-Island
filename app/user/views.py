from flask import render_template, session, redirect, url_for

from . import user 
from app.user.user_form import LoginForm


@user.route('/user/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['password'] = form.password.data
        if session['name'] == 'mapan':
            return redirect(url_for('admin.index'))
        return redirect(url_for('main.index'))
    return render_template('user/login.html', form=form)
