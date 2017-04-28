import os
import functools

from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required, current_user

from app.admin import admin
from app.models import Article
from config import Config


def admin_required(func):
    """只有管理员可以进行func处理"""
    @functools.wraps(func)
    def wrapper(*args, **kw):
        if current_user.is_admin:
            return func(*args, **kw)
        else:
            return render_template('403.html')
    return wrapper

@admin.route('/admin')
@login_required
@admin_required
def index():
    # 获取已记录文件集合
    loged_articles = Article.query.all()
    # 获取存在的md文件的name集合
    existed_md_articles = set()
    for md_name in os.listdir(Config.ARTICLES_SOURCE_DIR):
        existed_md_articles.add(md_name.split('.')[0])
    return render_template('admin.html',
                           loged_articles=loged_articles,
                           existed_md_articles=existed_md_articles)

@admin.route('/admin/upload', methods=['POST'])
@login_required
@admin_required
def upload():
    file = request.files['file']
    if file and Config.allowed_file(file.filename):
        filename = file.filename
        # 保存md文件
        file.save(os.path.join(Config.ARTICLES_SOURCE_DIR, filename))
        # 生成html与数据库记录
        Article.render_md(name=filename.rsplit('.')[0])

        flash("upload %s secceed" % filename)
    else:
        flash("upload %s failed" % filename)
    return redirect(url_for('admin.index'))

@admin.route('/admin/render/<article_name>')
@login_required
@admin_required
def render(article_name):
    flash(Article.render(article_name))
    return redirect(url_for('admin.index'))

@admin.route('/admin/refresh/<article_name>')
@login_required
@admin_required
def refresh(article_name):
    flash(Article.refresh(article_name))
    return redirect(url_for('admin.index'))

@admin.route('/admin/delete/md/<article_name>')
@login_required
@admin_required
def delete_md(article_name):
    flash(Article.delete_md(article_name))
    return redirect(url_for('admin.index'))

@admin.route('/admin/delete/html/<article_name>')
@login_required
@admin_required
def delete_html(article_name):
    flash(Article.delete_html(article_name))
    return redirect(url_for('admin.index'))

@admin.route('/admin/refresh_all')
@login_required
@admin_required
def refresh_all():
    """md文件改变则更新，不存在则生成"""
    Article.refresh_all_articles()
    return "Refresh all articles succeeded"
