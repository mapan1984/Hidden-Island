import os

from flask import request, redirect, url_for, render_template, \
                  flash, current_app
from flask_login import login_required, current_user

from app.admin import admin
from app.models import Article
from app.decorators import admin_required
from config import Config


@admin.route('/admin')
@login_required
@admin_required
def index():
    # 获取已记录文件集合
    loged_articles = Article.query.all()
    # 获取存在的md文件的name集合
    existed_md_articles = set()
    for md_name in os.listdir(current_app.config['ARTICLES_SOURCE_DIR']):
        existed_md_articles.add(md_name.split('.')[0])
    # 获取未被记录的md文件name的集合
    not_loged_articles = existed_md_articles\
                         - {article.name for article in loged_articles}
    return render_template('admin.html',
                           loged_articles=loged_articles,
                           not_loged_articles=not_loged_articles)

@admin.route('/admin/upload', methods=['POST'])
@login_required
@admin_required
def upload():
    file = request.files['file']
    if file and Config.allowed_file(file.filename):
        filename = file.filename
        # 保存md文件
        file.save(os.path.join(current_app.config['ARTICLES_SOURCE_DIR'],
                               filename))
        # 生成html与数据库记录
        Article.render(name=filename.rsplit('.')[0])

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
    article = Article.query.filter_by(name=article_name).first()
    return article.refresh()

@admin.route('/admin/delete/md/<article_name>')
@login_required
@admin_required
def delete_md(article_name):
    article = Article.query.filter_by(name=article_name).first()
    flash(article.delete_md())
    return redirect(url_for('admin.index'))

@admin.route('/admin/delete/html/<article_name>')
@login_required
@admin_required
def delete_html(article_name):
    print(article_name)
    article = Article.query.filter_by(name=article_name).first()
    flash(article.delete_html())
    return redirect(url_for('admin.index'))

@admin.route('/admin/refresh_all')
@login_required
@admin_required
def refresh_all():
    Article.refresh_all()
    return "Refresh all articles succeeded"

@admin.route('/admin/render_all')
@login_required
@admin_required
def render_all():
    Article.render_all()
    flash("Render all articles succeeded")
    return redirect(url_for('admin.index'))

