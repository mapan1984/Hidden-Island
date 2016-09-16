""" 
将articles中的markdown文件转为html文件，
放置在'app/templates/articles'目录中
"""

import os

import markdown
from jinja2 import Environment, FileSystemLoader

base_dir = os.path.abspath(os.path.dirname(__file__))
source_dir = base_dir + '\\articles\\'
target_dir = base_dir + '\\app\\templates\\articles\\'
layout_dir= base_dir + '\\app\\templates\\_layouts'


# markdown
md = markdown.Markdown(
    extensions=[
        "markdown.extensions.codehilite(css_class=highlight,linenums=None)",
        "markdown.extensions.meta",
        "markdown.extensions.tables",
        "markdown.extensions.toc",
    ]
)

# jinja
env = Environment(loader=FileSystemLoader(layout_dir))
template = env.get_template("article.html")

for article in os.listdir(source_dir):
    # 文章名
    article_name = article.split('.')[0]
    # 解析markdown文件
    with open(source_dir+article, "r") as fd:
        content_html = md.convert(fd.read())
        html = template.render(post_content=content_html)
    # 保存解析好的html文件
    with open(target_dir+post_name+'.html', "w") as fd:
        fd.write(html)
