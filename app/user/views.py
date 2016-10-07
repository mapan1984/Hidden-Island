from flask import render_template, session, redirect, url_for

from app.user.user_form import LoginForm

from . import user 

@user.route('/user/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['password'] = form.password.data
        return redirect(url_for('main.index'))
    return render_template('user/login.html', form=form)
