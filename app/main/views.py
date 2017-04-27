from sqlalchemy import desc
from flask import render_template, redirect, url_for

from app.main import main
from app.models import Category, Tag, Article

@main.route('/')
def index():
    return redirect(url_for('main.index_with_num', page_num=1))

@main.route('/<int:page_num>')
def index_with_num(page_num=None):
    """主页
    argv:
        page_num: 页号
    """
    if page_num is None:
        page_num = 1
    size = 2
    start = size*(page_num - 1)
    content_list = []
    for article in Article.query.order_by(desc(Article.date))\
                                .offset(start)\
                                .limit(size).all():
        with open(article.ds_path, "r", encoding='utf-8') as fd:
            content_list.append(fd.read())
    content = "".join(content_list)
    return render_template('index.html',
                           page_num=page_num,
                           content=content)

@main.route('/<article_name>')
def show_article(article_name):
    """ 显示单篇文章
    argv:
        article_name: 文件名(xxx)
    """
    article = Article.query.filter_by(name=article_name).first_or_404()
    with open(article.ds_path, "r", encoding='utf-8') as fd:
        content = fd.read()
    return render_template('article.html', content=content)

@main.route('/categories')
def categories():
    return render_template('category.html',
                           categories=Category.query.all())

@main.route('/tags')
def tags():
    return render_template('tag.html',
                           tags=Tag.query.all())

@main.route('/news')
def news():
    return render_template('news.html')

@main.route('/about')
def about():
    return render_template('about.html')
