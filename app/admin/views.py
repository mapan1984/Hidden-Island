import os

from flask import render_template, current_app, session

from app.admin import admin
from app.models import Article

@admin.route('/admin')
def index():
    return render_template('admin.html')

@admin.route('/admin/refresh')
def refresh():
    """md文件改变则更新，不存在则生成"""
    Article.refresh()
    return render_template('admin.html')
