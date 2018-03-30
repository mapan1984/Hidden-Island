from flask import abort, request, render_template, current_app, \
                  url_for, flash, redirect
from flask_login import login_required, current_user

from app import db
from app.user import user as user_blueprit
from app.models import User
from app.user.forms import EditProfileForm


@user_blueprit.route('/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)

    page = request.args.get('page', 1, type=int)
    pagination = user.articles.paginate(
            page, per_page=current_app.config['ARTICLES_PAGINATE'],
            error_out=False)
    articles = []
    for article in pagination.items:
        articles.append(article)
    return render_template('user/user.html', user=user,
                           pagination=pagination, articles=articles)


@user_blueprit.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('你的个人信息已被更新')
        return redirect(url_for('user.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('user/edit.html', form=form)
