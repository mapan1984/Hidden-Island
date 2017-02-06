import os
import functools

from flask import request, render_template, flash
from flask_login import login_required, current_user

from app import db
from app.admin import admin
from app.models import Article, Category
from app.generate import generate_article
from config import Config

ALLOWED_EXTENSIONS = set(['md', 'markdown'])

def allowed_file(filename):
    return '.' in filename \
            and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def admin_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        if current_user.is_admin:
            return func(*args, **kw)
        else:
            return render_template('403.html')
    return wrapper

def return_admin_index(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        func(*args, **kw)
        # 返回admin的主页
        category_articles = {}
        for category in Category.query.all():
            category_articles[category] = \
                    Article.query.filter_by(category=category).all()
        return render_template('admin.html',
                               category_articles=category_articles)
    return wrapper

@admin.route('/admin')
@login_required
@admin_required
def index():
    category_articles = {}
    for category in Category.query.all():
        category_articles[category] = \
                Article.query.filter_by(category=category).all()
    return render_template('admin.html',
                           category_articles=category_articles)

@admin.route('/admin/refresh')
@login_required
@admin_required
def refresh():
    """md文件改变则更新，不存在则生成"""
    Article.refresh()
    return "Refresh succeeded"

@admin.route('/admin/upload', methods=['POST'])
@login_required
@admin_required
@return_admin_index
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = file.filename
        file.save(os.path.join(Config.ARTICLES_SOURCE_DIR, filename))
        # 添加记录
        print("%s is added" % filename)
        article = Article(name=filename.rsplit('.')[0])
        article.md5 = article.get_md5()
        db.session.add(article)

        # 生成html文件
        generate_article(article)

        flash("upload %s secceed" % filename)
    else:
        flash("upload %s failed" % filename)

@admin.route('/admin/delete/<article_name>')
@login_required
@admin_required
@return_admin_index
def delete(article_name):
    article = Article.query.filter_by(name=article_name).first()
    if article:
        os.remove(article.sc_path)
        os.remove(article.ds_path)
        db.session.delete(article)
        flash("The {file} article was successfully deleted.".format(file=article_name))
    else:
        flash("The {file} article does not exist.".format(file=article_name))

