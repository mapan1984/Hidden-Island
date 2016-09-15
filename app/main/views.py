import os


from flask import render_template
from . import main


basedir = os.path.abspath(os.path.dirname(__file__))
targetdir = "\\".join(basedir.split('\\')[0:-1] + ['templates', 'post'])

@main.route('/')
def index():
    post_list = os.listdir(targetdir)
    return render_template('index.html', post_list=post_list)

@main.route('/templates/post/<page_name>')
def page(page_name):
    return render_template('post/'+page_name)
