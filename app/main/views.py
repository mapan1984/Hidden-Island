import datetime

from flask import render_template, request, flash, redirect, url_for, \
                  current_app, abort
from flask_login import current_user, login_required

from app import db
from app.main import main
from app.decorators import author_required
from app.sim import similarity
from app.main.forms import CommentForm, EditProfileForm, EditArticleForm
from app.models import Category, Tag, Article, Comment, Permission, User


@main.app_context_processor
def inject_permissions():
    """将Permission类加入模板上下文"""
    return dict(Permission=Permission)


@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.paginate(
            page, per_page=current_app.config['ARTICLES_PAGINATE'],
            error_out=False)
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
                           article=article)

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

    page = request.args.get('page', 1, type=int)
    pagination = user.articles.paginate(
            page, per_page=current_app.config['ARTICLES_PAGINATE'],
            error_out=False)
    articles = []
    for article in pagination.items:
        articles.append(article)
    return render_template('user.html', user=user,
                           pagination=pagination, articles=articles)


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


@main.route('/edit-article', methods=['GET', 'POST'])
@author_required
def edit_article():
    form = EditArticleForm()
    if current_user.can(Permission.WRITE_ARTICLES) \
            and form.validate_on_submit():
        article = Article(title=form.title.data,
                          name=form.title.data,
                          body=form.body.data,
                          date=datetime.date.today(),
                          author=current_user._get_current_object())
        category=Category.query.get(form.category.data)
        article.change_category(category)
        article.delete_tags()
        article.add_tags(form.tags.data.split(' '))
        db.session.add(article)
        return redirect(url_for('main.article', article_name=article.name))
    return render_template('edit_article.html', form=form)


@main.route('/delete-article/<article_name>')
@author_required
def delete_article(article_name):
    article = Article.query.filter_by(name=article_name).first_or_404()
    if current_user != article.author \
            and not current_user.can(Permission.ADMINISTER):
        abort(403)
    else:
        flash(article.delete_html())
        return redirect(request.args.get('next')
                    or url_for('main.user', username=current_user.username))


@main.route('/modify-article/<article_name>', methods=['GET', 'POST'])
@author_required
def modify_article(article_name):
    article = Article.query.filter_by(name=article_name).first_or_404()
    form = EditArticleForm(article=article)
    if current_user != article.author \
            and not current_user.can(Permission.ADMINISTER):
        abort(403)
    if current_user.can(Permission.WRITE_ARTICLES) \
            and form.validate_on_submit():
        article.title = form.title.data
        if article.name is None:
            article.name = form.title.data
        article.body = form.body.data

        category=Category.query.get(form.category.data)
        article.change_category(category)

        article.delete_tags()
        article.add_tags(form.tags.data.split(' '))

        db.session.add(article)
        flash('You article has been modified.')
        return redirect(url_for('main.article', article_name=article.name))
    form.title.data = article.title
    form.category.data = article.category.id
    form.tags.data = " ".join(tag.name for tag in article.tags)
    form.body.data = article.body
    return render_template('edit_article.html', form=form)


@main.route('/search', methods=['POST'])
def search():
    articles = []
    keys = request.form['keys']
    for article in Article.query.all():
        article_content = "".join([article.body]
                                  + [article.title]*3
                                  + [article.category.name]*3
                                  + [tag.name for tag in article.tags]*3)
        sim = similarity(article_content, keys)
        articles.append((sim, article))
    articles.sort(key=lambda x:x[0], reverse=True)
    return render_template('search.html', articles=articles[:20])

