import os

from flask import request, render_template, flash
from flask_login import login_required

from app import db
from app.admin import admin
from app.models import Article
from app.generate import generate_article
from config import Config

ALLOWED_EXTENSIONS = set(['md', 'markdown'])

def allowed_file(filename):
    return '.' in filename \
            and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@admin.route('/admin')
@login_required
def index():
    return render_template('admin.html')

@admin.route('/admin/refresh')
@login_required
def refresh():
    """md文件改变则更新，不存在则生成"""
    Article.refresh()
    return "Refresh succeeded"

@admin.route('/admin/upload/', methods=['POST'])
@login_required
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = file.filename
        file.save(os.path.join(Config.ARTICLES_SOURCE_DIR, filename))
        # 添加记录
        print("%s is added" % filename)
        article = Article(name=filename.rsplit('.')[0])
        article.md5 = article._get_md5()
        db.session.add(article)

        # 生成html文件
        generate_article(article.sc_path, article.ds_path)

        flash("upload %s secceed" % filename)
        return render_template('admin.html')
    else:
        flash("upload %s failed" % filename)
        return render_template('admin.html')
