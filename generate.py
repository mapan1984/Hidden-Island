""" 
将post中的markdown文件转为html文件，
放置在'app/templates/post'目录中
"""

import os

import markdown
from jinja2 import Environment, FileSystemLoader

basedir = os.path.abspath(os.path.dirname(__file__))
sourcedir = basedir + '\\post\\'
targetdir = basedir + '\\app\\templates\\post\\'
layoutdir= basedir + '\\app\\templates\\_layouts'


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
env = Environment(loader=FileSystemLoader(layoutdir))
template = env.get_template("post.html")

for post in os.listdir(sourcedir):
    # 文章名
    post_name = post.split('.')[0]

    with open(sourcedir+post, "r") as p:
        content_html = md.convert(p.read())
        html = template.render(post_content=content_html)
    with open(targetdir+post_name+'.html', "w") as p:
        p.write(html)
