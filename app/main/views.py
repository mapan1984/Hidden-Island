import os

from flask import render_template
from . import main

base_dir = os.path.abspath(os.path.dirname(__file__))
articles_dir = "\\".join(base_dir.split('\\')[0:-2] + ['articles'])

@main.route('/')
def index():
    articles_list = os.listdir(articles_dir)
    return render_template('index.html', articles_list=articles_list)
