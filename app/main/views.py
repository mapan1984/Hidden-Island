import os

from flask import render_template, current_app, session

from . import main

@main.route('/')
def index():
    page_num = 1
    start = 3*page_num - 3
    end = 3*page_num - 1
    log = current_app.config['LOG']
    content_list = []
    for article in log.article_list[start:end]:
        with open(article.ds_path, "r", encoding='utf-8') as fd:
            content_list.append(fd.read())
    content = "".join(content_list)
    return render_template('index.html',
                           page_num=page_num,
                           content=content,
                           name=session.get('name'))

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
