from app import create_app, db
from app.models import Article, Role, User
from app.utils.markdown import MD
from app.utils.convert import todatetime


from .utils import get_articles_info
from .config import ARTICLES_PATH


def log_md(category_name, article_name, content):
    """将文章记录至数据库
    Args:
        category_name <str>: 目录名
        article_name <str>: 文件名
        content <str>: 文件内容
    """
    article = Article()

    article.body = content
    article.body_html = MD.convert(content)
    article.title = MD.Meta.get('title')
    article.name = article.title
    article.timestamp = todatetime(article_name)

    admin_role = Role.query.filter_by(permissions=0xff).first()
    article.author = User.query.filter_by(role=admin_role).first()

    tag_names = MD.Meta.get('tags')

    try:
        article.change_category(category_name)
        article.add_tags(tag_names)
        db.session.add(article)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return False
    else:
        return True


def fetch_article(article_path):
    """读取文章内容并返回"""
    with open(article_path, encoding='utf-8') as fd:
        content = fd.read()
    return content


def work(article_info):
    """读取文章内容，记录至数据库
    Args:
        article_info: (category_name, article_path)
    """
    category_name, article_path = article_info
    content = fetch_article(str(article_path))
    article_name = article_path.name

    print(f'logging {article_name}...')
    if log_md(category_name, article_name, content):
        print(f'{article_name} logged.')
    else:
        print(f'{article_name} may be aready logged.')


if __name__ == '__main__':
    articles_info = get_articles_info(ARTICLES_PATH)
    app = create_app('development')
    with app.app_context():
        for article_info in articles_info:
            work(article_info)
