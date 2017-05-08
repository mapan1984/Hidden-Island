from flask import render_template, request, redirect, url_for

from config import Config
from app.main import main
from app.models import Category, Tag, Article

@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.paginate(
            page, per_page=Config.PAGINATE, error_out=False)
    contents = []
    for article in pagination.items:
        contents.append(article.body)
    return render_template('index.html',
                           page_num=page,
                           contents=contents,
                           pagination=pagination,
                           articles=Article.query.limit(10).all())

@main.route('/<article_name>')
def show_article(article_name):
    """ 显示单篇文章
    argv:
        article_name: 文件名(xxx)
    """
    article = Article.query.filter_by(name=article_name).first_or_404()
    return render_template('article.html', content=article.body)

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

@main.route('/about')
def about():
    return render_template('about.html')
