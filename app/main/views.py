from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required

from app import db
from config import Config
from app.main import main
from app.main.forms import CommentForm, EditProfileForm
from app.models import Category, Tag, Article, Comment, Permission, User


@main.app_context_processor
def inject_permissions():
    """将Permission类加入模板上下文"""
    return dict(Permission=Permission)


@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.paginate(
            page, per_page=Config.ARTICLES_PAGINATE, error_out=False)
    articles = []
    for article in pagination.items:
        articles.append(article)
    return render_template('index.html',
                           pagination=pagination,
                           articles=articles,
                           archives=Article.query.limit(10).all())


@main.route('/<article_name>', methods=['GET', 'POST'])
def article(article_name):
    """ 显示单篇文章
    argv:
        article_name: 文件名(xxx)
    """
    article = Article.query.filter_by(name=article_name).first_or_404()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          article=article,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('You comment has been published.')
        return redirect(url_for('main.article', article_name=article.name))
    return render_template('article.html',
                           form=form,
                           article_name=article.name,
                           content=article.body,
                           comments=article.comments)


@main.route('/categories')
def categories():
    return render_template('category.html',
                           categories=Category.query.all())


@main.route('/tags')
def tags():
    return render_template('tag.html',
                           tags=Tag.query.all())


@main.route('/archives')
def archives():
    return render_template('archives.html',
                           articles=Article.query.all())


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

