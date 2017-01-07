import os

from flask import render_template, current_app, redirect, url_for

from app.article import article
from app.models import Article

@article.route('/article/<article_name>')
def post(article_name):
    """ 显示单篇文章
    argv:
        article_name: 文件名(xxx)
    """
    article = Article.query.filter_by(name=article_name).first()
    return render_template('articles/'+article.html_name)

@article.route('/article/page/<int:page_num>')
def page_with_num(page_num):
    """ 显示多篇文章
    argv:
        page_num: 页号
    """
    if page_num == 1:
        return redirect(url_for('main.index'))
    start, end = 2*page_num - 2, 2*page_num
    content_list = []
    for article in Article.query.all()[start:end]:
        with open(article.ds_path, "r", encoding='utf-8') as fd:
            content_list.append(fd.read())
    content = "".join(content_list)
    return render_template('index.html',
                           page_num=page_num,
                           content=content)
