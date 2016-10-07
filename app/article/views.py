import os

import markdown
from flask import render_template, current_app

from app.file_name import FileName

from . import article


# markdown
md = markdown.Markdown(
    extensions=[
        "markdown.extensions.codehilite(css_class=highlight,linenums=None)",
        "markdown.extensions.meta",
        "markdown.extensions.tables",
        "markdown.extensions.toc",
    ]
)

def html_exists(file):
    '''
    argv:
        article: xxx.md
    return:
        if xxx.html is exists:
            return True
        else:
            return False
    '''
    if os.path.exists(file.ds_path):
        return True
    else:
        return False

def generate(file, monitor):
    if html_exists(file):
        print("%s is exist" % file.name)
        if monitor.is_change(file.md_name):
            print("%s is changed" % file.name)
            with open(file.sc_path, "r") as fd:
                article_content = md.convert(fd.read())
                destination_html = render_template('_layouts/article.html',
                               article_content=article_content)
            with open(file.ds_path, "w") as fd:
                fd.write(destination_html)
    else:
        print("%s is not exist" % file.name)
        with open(file.sc_path, "r") as fd:
            article_content = md.convert(fd.read())
            destination_html = render_template('_layouts/article.html',
                           article_content=article_content)
        with open(file.ds_path, "w") as fd:
            fd.write(destination_html)

@article.route('/article/<article>')
def page(article):
    '''
    argv:
        article: xxx
    '''
    file = FileName(article)
    monitor = current_app.config['MONITOR']
    generate(file, monitor)
    return render_template('articles/'+file.html_name)
