from flask import request, jsonify
from app import db
from app.api import api
from app.models import Comment, Article


@api.route('/comments')
def comments():
    comments = [comment.to_json() for comment in Comment.query.all()]
    return jsonify(comments)


@api.route('/article/<int:id>/comments', methods=['GET', 'POST'])
def aritcle_comments(id):
    print(id)
    if request.method == 'POST':
        new_comment = request.form.to_dict()
        db.session.add(Comment.from_json(new_comment))

    article = Article.query.get(id)
    comments = [comment.to_json() for comment in Comment.query.filter_by(article=article).all()]
    return jsonify(comments)

