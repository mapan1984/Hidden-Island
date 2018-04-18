from flask import render_template, request, current_app

from app.main import main
from app.utils.similarity import similarity
from app.models import Category, Tag, Article, Permission


@main.app_context_processor
def inject_permissions():
    """将Permission类加入模板上下文"""
    return dict(Permission=Permission)


@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.paginate(
        page,
        per_page=current_app.config['ARTICLES_PAGINATE'],
        error_out=False
    )

    articles = [article for article in pagination.items]

    archives_anchor = []
    for index, ((year, month), articls) in enumerate(Article.archives()):
        if index > 10:
            break
        archives_anchor.append(f'{year}-{month}')

    return render_template(
        'index.html',
        articles=articles,
        pagination=pagination,
        archives_anchor=archives_anchor,
    )


@main.route('/categories')
def categories():
    return render_template(
        'category.html',
        categories=Category.query.all()
    )


@main.route('/tags')
def tags():
    return render_template(
        'tag.html',
        tags=Tag.query.all()
    )


@main.route('/archives')
def archives():
    return render_template(
        'archives.html',
        archives=Article.archives()
    )


@main.route('/search', methods=['POST'])
def search():
    articles = []
    keys = request.form['keys']
    for article in Article.query.all():
        article_content = "".join([article.body]
                                  + [article.title] * 3
                                  + [article.category.name] * 3
                                  + [tag.name for tag in article.tags] * 3)
        sim = similarity(article_content, keys)
        articles.append((sim, article))
    articles.sort(key=lambda x: x[0], reverse=True)

    archives_anchor = []
    for index, ((year, month), articls) in enumerate(Article.archives()):
        if index > 10:
            break
        archives_anchor.append(f'{year}-{month}')

    return render_template(
        'search.html',
        articles=articles[:8],
        archives_anchor=archives_anchor,
    )
