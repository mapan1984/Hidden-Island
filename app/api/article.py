from flask import jsonify, request, g, url_for, current_app
from app.models import Article

from app import db
from app.models import Permission
from app.api import api
from app.api.decorators import permission_required
from app.api.errors import forbidden, ValidationError


@api.route('/articles/<int:id>')
def get_article(id):
    article = Article.query.get_or_404(id)
    return jsonify(article.to_json())


@api.route('/articles/')
def get_articles():
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.paginate(
        page, per_page=current_app.config['ARTICLES_PAGINATE'],
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
def new_article():
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
    # XXX: 建立文章索引应在后台进行
    # article._build_index()
    # article._cache_similar()
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
    # XXX: 建立文章索引应在后台进行
    article._build_index()
    article._cache_similar()
    return (
        # 201 - 已创建
        jsonify(article.to_json()),
        201,
        {'Location': url_for('api.get_article', id=article.id, _external=True)}
    )


@api.route('/articles/<int:article_id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    if g.current_user != article.author \
            and not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    article.body = request.json.get('body', article.body)
    db.session.add(article)
    # XXX: 建立文章索引应在后台进行
    # article._build_index()
    # article._cache_similar()
    return jsonify(article.to_json())
