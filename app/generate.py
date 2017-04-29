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
    [_, month, day, _, _, year] = date.split(' ')
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
    with open(article.sc_path, "r", encoding="utf-8") as scfd,\
         open(article.ds_path, "w", encoding="utf-8") as dsfd:
        article_content = MD.convert(scfd.read())
        name = article.name
        title = MD.Meta.get('title')[0]
        datestr = MD.Meta.get('date')[0]
        date = convert_date(datestr)
        category_name = MD.Meta.get('category')[0]
        tag_names = MD.Meta.get('tag')

        article.title = title
        article.datestr = datestr
        article.date = date

        category = Category.query.filter_by(name=category_name).first()
        if category is None:
            category = Category(name=category_name, size=0)
        category.size += 1
        db.session.add(category)
        article.category = category

        for tag in article.tags.all():
            tag.size -= 1
            article.tags.remove(tag)
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag is None:
                tag = Tag(name=tag_name, size=0)
            tag.size += 1
            db.session.add(tag)
            article.tags.append(tag)
        for tag in Tag.query.all():
            if tag.size == 0:
                de.session.delete(tag)

        db.session.add(article)
        db.session.commit()

        destination_html = render_template('_layouts/content.html',
                                           name=name,
                                           title=title,
                                           datestr=datestr,
                                           category=category_name,
                                           tags=tag_names,
                                           article_content=article_content)
        dsfd.write(destination_html)
