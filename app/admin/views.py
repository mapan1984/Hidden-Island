import os

from flask import render_template, current_app

from . import admin
from app.article_info import Article
from app.article_log import ArticleLog
from app.generate import generate


@admin.route('/admin')
def index():
    return render_template('admin.html')

@admin.route('/admin/refresh')
def refresh():
    """ md文件改变则更新，不存在则生成 """
    log = ArticleLog(current_app.config['ARTICLES_SOURCE_DIR'])
    log.refresh()
    for article in log.article_list:
        if not os.path.exists(article.ds_path):
            print("%s is not exist" % article.html_name)
            generate(article)
        else:
            if log.is_change(article):
                print("%s is changed" % article.md_name)
                generate(article)
            else:
                print("%s is exist and %s is not changed"
                      % (article.html_name, article.md_name))
    return render_template('admin.html')
