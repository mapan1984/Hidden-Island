import markdown
from flask import render_template

# markdown
md = markdown.Markdown(
    extensions=[
        "markdown.extensions.codehilite(css_class=highlight,linenums=None)",
        "markdown.extensions.meta",
        "markdown.extensions.tables",
        "markdown.extensions.toc",
    ]
)

def generate_article(sc_path, ds_path):
    """根据md文件生成html文件"""
    with open(sc_path, "r", encoding="utf-8") as scf,\
         open(ds_path, "w", encoding="utf-8") as dsf:
        article_content = md.convert(scf.read())
        destination_html = render_template('_layouts/content.html',
                                           title=md.Meta.get('title'),
                                           summary=md.Meta.get('summary'),
                                           date=md.Meta.get('date'),
                                           tag=md.Meta.get('tag'),
                                           article_content=article_content)
        dsf.write(destination_html)
