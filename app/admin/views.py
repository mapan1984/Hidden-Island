import os

from flask import render_template, current_app

from app.file_name import FileName
from app.generate import generate

from . import admin


@admin.route('/admin')
def index():
    return render_template('admin.html')

@admin.route('/admin/refresh')
def refresh():
    """ md文件改变则更新，不存在则生成 """
    monitor = current_app.config['MONITOR']
    monitor.refresh_path()
    monitor.refresh_kv()
    monitor.refresh_log()
    for article_md_name in os.listdir(current_app.config['ARTICLES_SOURCE_DIR']):
        file = FileName(os.path.splitext(article_md_name)[0])
        if not os.path.exists(file.ds_path):
            print("%s is not exist" % file.html_name)
            generate(file)
        else:
            if monitor.is_change(file.md_name):
                print("%s is changed" % file.md_name)
                generate(file)
            else:
                print("%s is exist and %s is not changed" 
                      % (file.html_name, file.md_name))
    return render_template('admin.html')
