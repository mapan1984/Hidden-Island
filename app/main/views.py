import os

from flask import render_template, current_app, session

from . import main

@main.route('/')
def index():
    articles_list = [os.path.splitext(article_md_name)[0]
       for article_md_name in os.listdir(current_app.config['ARTICLES_SOURCE_DIR'])]
    return render_template('index.html', articles_list=articles_list,
                                         name=session.get('name'))
