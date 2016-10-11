import os

from flask import render_template

from . import article
from app.article_info import Article
from app.generate import generate


@article.route('/article/<article_name>')
def page(article_name):
    """
    argv:
        article_name: 文件名(xxx)
    """
    article = Article(article_name)
    if not os.path.exists(article.ds_path):
        generate(article)
    return render_template('articles/'+article.html_name)
