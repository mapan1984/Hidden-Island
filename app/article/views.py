import os

from flask import render_template, current_app
import markdown

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

@article.route('/article/<article_name>')
def page(article_name):
    # 解析markdown文件
    article_path = os.path.join(current_app.config['ARTICLES_DIR'], article_name)
    with open(article_path, "r") as fd:
        article_content_html = md.convert(fd.read())
    return render_template('_layouts/article.html', 
                           article_content=article_content_html)
