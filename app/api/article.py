from flask import jsonify, request, g, url_for, current_app
from app.models import Article

from app import db
from app.models import Permission
from app.api import api
from app.api.decorators import permission_required
from app.api.errors import forbidden, ValidationError


@api.route('/article/<int:id>')
def get_article(id):
    article = Article.query.get_or_404(id)
    return jsonify(article.to_json())


@api.route('/articles/')
def get_articles():
    articles = Article.query.all()
    return jsonify({
        'articles': [article.to_json() for article in articles]
    })


@api.route('/article/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_article():
    try:
        article = Article.from_json(request.json)
    except ValidationError as exp:
        # 无内容，412 - 未满足前提条件
        current_app.logger.warning(str(exp))
        return (
            jsonify({'error': str(exp)}),
        )
    article.author = g.current_user
    db.session.add(article)
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
    return (
        # 201 - 已创建
        jsonify(article.to_json()),
        201,
        {'Location': url_for('api.get_article', id=article.id, _external=True)}
    )


@api.route('/article/<int:article_id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    if g.current_user != article.author \
            and not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    article.body = request.json.get('body', article.body)
    db.session.add(article)
    return jsonify(article.to_json())
