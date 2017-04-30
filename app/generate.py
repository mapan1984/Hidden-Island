import markdown
import datetime
from flask import render_template

from app import db
from app.models import Category, Tag

month_map = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}

# Thu Apr 27 21:24:32 CST 2017 --> 2017-4-27
def convert_date(date):
    _, month, day, _, _, year = date.split(' ')
    month = month_map[month]
    return datetime.date(int(year), month, int(day))

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
    with open(article.sc_path, "r", encoding="utf-8") as scfd:
        article_content = MD.convert(scfd.read())

    title         = MD.Meta.get('title')[0]
    datestr       = MD.Meta.get('date')[0]
    date          = convert_date(datestr)
    category_name = MD.Meta.get('category')[0]
    tag_names     = MD.Meta.get('tag')

    article.title   = title
    article.datestr = datestr
    article.date    = date

    article.change_category(category_name)

    article.delete_tags()
    article.add_tags(tag_names)

    db.session.add(article)

    destination_html = render_template('_layouts/content.html',
                                       name=article.name,
                                       title=title,
                                       datestr=datestr,
                                       category=category_name,
                                       tags=tag_names,
                                       article_content=article_content)
    with open(article.ds_path, "w", encoding="utf-8") as dsfd:
        dsfd.write(destination_html)
