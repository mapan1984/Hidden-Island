import os

from flask import render_template, current_app, session

from app.main import main
from app.models import Article

@main.route('/')
def index():
    """主页"""
    page_num = 1
    start, end = 2*page_num - 2, 2*page_num
    content_list = []
    for article in Article.query.all()[start:end]:
        with open(article.ds_path, "r", encoding='utf-8') as fd:
            content_list.append(fd.read())
    content = "".join(content_list)
    return render_template('index.html',
                           page_num=page_num,
                           content=content)

@main.route('/category')
def category():
    return 'category'

@main.route('/tag')
def tag():
    return 'tag'

@main.route('/new')
def new():
    return 'new'

@main.route('/about')
def about():
    return 'about'
