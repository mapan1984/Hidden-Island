import os

from flask import render_template

from app.file_name import FileName
from app.generate import generate

from . import article

@article.route('/article/<article>')
def page(article):
    '''
    argv:
        article: 文件名(xxx)
    '''
    file = FileName(article)
    if not os.path.exists(file.ds_path):
        generate(file)
    return render_template('articles/'+file.html_name)
