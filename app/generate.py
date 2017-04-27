import markdown
from flask import render_template

from app import db
from app.models import Category, Tag

# markdown
MD = markdown.Markdown(
    extensions=[
        "markdown.extensions.codehilite(css_class=highlight,linenums=None)",
        "markdown.extensions.meta",
        "markdown.extensions.tables",
        "markdown.extensions.toc",
    ]
)

def generate_article(article):
    """根据md文件生成html文件
    article: 数据库中article类型
    """
    with open(article.sc_path, "r", encoding="utf-8") as scfd,\
         open(article.ds_path, "w", encoding="utf-8") as dsfd:
        article_content = MD.convert(scfd.read())
        category_name = MD.Meta.get('category')[0]
        tag_name = MD.Meta.get('tag')[0]

        category = Category.query.filter_by(name=category_name).first()
        if category is None:
            category = Category(name=category_name)
            db.session.add(category)

        tag = Tag.query.filter_by(name=tag_name).first()
        if tag is None:
            tag = Tag(name=tag_name)
            db.session.add(tag)

        article.category = category
        article.tag = tag
        db.session.add(article)

        db.session.commit()

        destination_html = render_template('_layouts/content.html',
                                           title=MD.Meta.get('title')[0],
                                           date=MD.Meta.get('date')[0],
                                           category=category_name,
                                           tag=tag_name,
                                           article_content=article_content)
        dsfd.write(destination_html)
