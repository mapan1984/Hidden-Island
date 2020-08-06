from flask import request, jsonify, current_app, url_for
from flask_login import current_user

from app import db
from app.api import api
from app.models import Comment, Article, Permission
from app.api.decorators import permission_required, login_required


@api.route('/comments/')
def get_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_comments', page=page + 1)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())


@api.route('/articles/<int:id>/comments/', methods=['GET'])
def get_article_comments(id):
    article = Article.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = article.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_article_comments', id=id, page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_article_comments', id=id, page=page + 1)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/articles/<int:id>/comments/', methods=['POST'])
@login_required
@permission_required(Permission.COMMENT)
def new_article_comment(id):
    article = Article.query.get_or_404(id)
    request.json['author_id'] = current_user.id
    request.json['article_id'] = article.id
    comment = Comment.from_json(request.json)
    db.session.add(comment)
    db.session.commit()
    return (
        jsonify(comment.to_json()),
        201,
        {'Location': url_for('api.get_comment', id=comment.id)}
    )
