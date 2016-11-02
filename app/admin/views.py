import os

from flask import render_template, current_app, session
from flask_login import login_required

from app.admin import admin
from app.models import Article

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
