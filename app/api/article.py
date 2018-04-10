from flask import jsonify
from app.models import Article

from app.api import api


@api.route('/article/<int:id>')
def get_article(id):
    article = Article.query.get_or_404(id)
    return jsonify(article.to_json())
