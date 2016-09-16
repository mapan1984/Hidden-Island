import os

from flask import render_template, current_app
from . import main

@main.route('/')
def index():
    articles_list = os.listdir(current_app.config['ARTICLES_DIR'])
    return render_template('index.html', articles_list=articles_list)
