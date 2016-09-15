import os

from flask import render_template
import markdown

from . import article

base_dir = os.path.abspath(os.path.dirname(__file__))
articles_dir = '\\'.join(base_dir.split('\\')[0:-2] + ['articles'])

# markdown
md = markdown.Markdown(
    extensions=[
        "markdown.extensions.codehilite(css_class=highlight,linenums=None)",
        "markdown.extensions.meta",
        "markdown.extensions.tables",
        "markdown.extensions.toc",
    ]
)

@article.route('/article/<article_name>')
def page(article_name):
    with open(articles_dir+'\\'+article_name, "r") as fd:
        article_content_html = md.convert(fd.read())
    return render_template('_layouts/article.html', article_content=article_content_html)
