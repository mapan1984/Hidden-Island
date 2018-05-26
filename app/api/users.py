from flask import jsonify, request, current_app, url_for
from app.models import User, Article

from app.api import api


@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api.route('/users/<int:id>/articles/')
def get_user_articles(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.articles.order_by(Article.timestamp.desc()).paginate(
        page, per_page=current_app.config['ARTICLES_PAGINATE'],
        error_out=False
    )
    articles = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_articles', id=id, page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_articles', id=id, page=page + 1)
    return jsonify({
        'articles': [article.to_json() for article in articles],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

