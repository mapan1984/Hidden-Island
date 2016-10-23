import os

from flask import render_template, current_app, session

from app.admin import admin
from app.models import Article
from app.generate import generate


@admin.route('/admin')
def index():
    return render_template('admin.html')

@admin.route('/admin/refresh')
def refresh():
    """ md文件改变则更新，不存在则生成 """
    for article in Article.query.all():
        if not os.path.exists(article.ds_path):
            print("%s is not exist" % article.html_name)
            generate(article)
        else:
            if article.is_change():
                print("%s is changed" % article.md_name)
                generate(article)
            else:
                print("%s is exist and %s is not changed"
                      % (article.html_name, article.md_name))
    Article.refresh()
    return render_template('admin.html')
