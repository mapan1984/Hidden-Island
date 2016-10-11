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

def generate(file):
    """ 根据md文件生成html文件 """
    with open(file.sc_path, "r") as fd:
        article_content = md.convert(fd.read())
        destination_html = render_template('_layouts/article.html',
                                           title=md.Meta['title'],
                                           summary=md.Meta['summary'],
                                           date=md.Meta['date'],
                                           tag=md.Meta['tag'],
                                           article_content=article_content)

        print(md.Meta)
    with open(file.ds_path, "w") as fd:
        fd.write(destination_html)

#    md.convertFile(input=file.sc_path, output=file.ds_path)
