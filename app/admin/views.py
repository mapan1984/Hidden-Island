import os

from flask import request, render_template, current_app, session
from flask_login import login_required

from app.admin import admin
from app.models import Article
from config import Config

@admin.route('/admin')
@login_required
def index():
    return render_template('admin.html')

@admin.route('/admin/refresh')
@login_required
def refresh():
    """md文件改变则更新，不存在则生成"""
    Article.refresh()
    return render_template('admin.html')

ALLOWED_EXTENSIONS = set(['md', 'markdown'])

def allowed_file(filename):
    return '.' in filename \
            and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@admin.route('/admin/upload/', methods=['POST'])
@login_required
def upload():
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = file.filename
        file.save(os.path.join(Config.ARTICLES_SOURCE_DIR, filename))
        return "upload %s secceed" % filename
    else:
        return "upload %s failed" % filename

