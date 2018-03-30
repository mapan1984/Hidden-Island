from flask import render_template, request, current_app

from app.main import main
from app.sim import similarity
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
    return render_template(
        'index.html',
        pagination=pagination,
        articles=articles,
        archives=Article.query.limit(10).all()
    )



@main.route('/categories')
def categories():
    return render_template('category.html',
                           categories=Category.query.all())


@main.route('/tags')
def tags():
    return render_template('tag.html',
                           tags=Tag.query.all())


@main.route('/archives')
def archives():
    return render_template('archives.html',
                           articles=Article.query.all())



@main.route('/search', methods=['POST'])
def search():
    articles = []
    keys = request.form['keys']
    for article in Article.query.all():
        article_content = "".join([article.body]
                                  + [article.title]*3
                                  + [article.category.name]*3
                                  + [tag.name for tag in article.tags]*3)
        sim = similarity(article_content, keys)
        articles.append((sim, article))
    articles.sort(key=lambda x: x[0], reverse=True)
    return render_template('search.html', articles=articles[:20],
                           archives=Article.query.limit(10).all())
