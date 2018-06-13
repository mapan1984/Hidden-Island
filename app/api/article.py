from flask import jsonify, request, g, url_for, current_app
from app.models import Article

from app import db, redis
from app.models import Permission
from app.api import api
from app.api.decorators import permission_required
from app.api.errors import forbidden, ValidationError
from app.tasks import build_index, rebuild_index


@api.route('/articles/<int:id>')
def get_article(id):
    article = Article.query.get_or_404(id)
    return jsonify(article.to_json())


@api.route('/articles/')
def get_articles():
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.paginate(
        page, per_page=current_app.config['ARTICLES_PER_PAGE'],
        error_out=False
    )
    articles = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_articles', page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_articles', page=page + 1)
    return jsonify({
        'articles': [article.to_json() for article in articles],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/articles/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_article():
    try:
        article = Article.from_json(request.json)
    except ValidationError as exp:
        # 无内容，412 - 未满足前提条件
        current_app.logger.warning(str(exp))
        return (
            jsonify({'error': str(exp)}),
            412,
        )
    article.author = g.current_user
    db.session.add(article)
    db.session.commit()
    build_index.delay(article.id)
    return (
        # 201 - 已创建
        jsonify(article.to_json()),
        201,
        {'Location': url_for('api.get_article', id=article.id, _external=True)}
    )


@api.route('/sync-article/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def sync_article():
    try:
        article = Article.from_jekyll_json(request.json)
    except ValidationError as exp:
        # 无内容，412 - 未满足前提条件
        current_app.logger.warning(str(exp))
        return (
            jsonify({'error': str(exp)}),
            412,
        )
    # 标题冲突，409 - 冲突
    if not article:
        return (
            jsonify({'message': 'may be article exsited.'}),
            409
        )
    article.author = g.current_user
    db.session.add(article)
    db.session.commit()
    build_index.delay(article.id)
    return (
        # 201 - 已创建
        jsonify(article.to_json()),
        201,
        {'Location': url_for('api.get_article', id=article.id, _external=True)}
    )


@api.route('/articles/<int:article_id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def modify_article(article_id):
    article = Article.query.get_or_404(article_id)
    if g.current_user != article.author \
            and not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    # XXX: 现在只能更新body
    article.body = request.json.get('body', article.body)
    db.session.add(article)
    rebuild_index.delay(article.id)
    return jsonify(article.to_json())


@api.route('/articles/<int:id>/similarities/')
def get_similarities(id):
    article = Article.query.get_or_404(id)
    similarities = redis.zrevrange(article.title, 0, 4, withscores=True)
    result = [
        {
            'title': similarity[0],
            'url': url_for('article.article', title=similarity[0]),
            'similarity': similarity[1]
        } for similarity in similarities
    ]
    return jsonify(result)

