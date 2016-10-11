import os

from flask import render_template, current_app, redirect, url_for

from . import article
from app.article_info import Article
from app.generate import generate


@article.route('/article/<article_name>')
def post(article_name):
    """
    argv:
        article_name: 文件名(xxx)
    """
    article = Article(article_name)
    if not os.path.exists(article.ds_path):
        generate(article)
    return render_template('articles/'+article.html_name)

@article.route('/article/page/<int:page_num>')
def page(page_num):
    if page_num == 1:
        return redirect(url_for('main.index'))
    start = 3*page_num - 3
    end = 3*page_num -1
    log = current_app.config['LOG']
    content_list=[]
    for article in log.article_list[start:end]:
        with open(article.ds_path, "r", encoding='utf-8') as fd:
            content_list.append(fd.read())
    content="".join(content_list)
    return render_template('index.html', page_num=page_num,
                           content=content)
