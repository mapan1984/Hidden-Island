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

@article.route('/article/<article>')
def page(article):
    # 去除markdown文件扩展名(.md)，获取文件名
    article_name = os.path.splitext(article)[0]
    article_destination_path = os.path.join(
        current_app.config['ARTICLES_DESTINATION_DIR'], article_name+'.html')
    # 如果对应html文件已存在，直接使用html文件
    if os.path.exists(article_destination_path):
        return render_template('articles/'+article_name+'.html')
    else:
        # 找到请求的markdwon文件，解析markdown文件
        article_source_path = os.path.join(
            current_app.config['ARTICLES_SOURCE_DIR'], article)
        with open(article_source_path, "r") as fd:
            article_content_html = md.convert(fd.read())
            destination_html = render_template('_layouts/article.html',
                           article_content=article_content_html)
        with open(article_destination_path, "w") as fd:
            fd.write(destination_html)
        return destination_html