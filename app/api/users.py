import json
from collections import defaultdict

from flask import jsonify, request, current_app, url_for
from app.models import User, Article, Rating

from app.api import api
from app.utils.recommender import get_recommended_items, calculate_similar_items


@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api.route('/users/<int:id>/articles/')
def get_user_articles(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.articles.order_by(Article.timestamp.desc()).paginate(
        page, per_page=current_app.config['ARTICLES_PER_PAGE'],
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


@api.route('/users/<int:id>/recommendation/')
def get_recommendation(id):
    """ 获取推荐信息，依赖 person_prefs 和 item_prefs 字段"""
    # TODO: 缓存中间结果
    # with open('person_prefs.json', 'r') as fd:
    #     person_prefs = json.load(fd)
    # with open('item_prefs.json', 'r') as fd:
    #     item_prefs = json.load(fd)
    person_prefs = defaultdict(dict)
    item_prefs = defaultdict(dict)
    for rating in Rating.query.all():
        username = rating.user.username
        title = rating.article.title
        rating_value = rating.value
        person_prefs[username][title] = rating_value
        item_prefs[title][username] = rating_value

        # person_prefs.hset(username, article_name, rating_value)
        # item_prefs.hset(article_name, username, rating_value)

        print(f'Cache rattings of {title} & {username} := {rating_value}')

    user = User.query.get_or_404(id)

    item_match = calculate_similar_items(item_prefs)
    recommendations = get_recommended_items(person_prefs, item_match, user.username)[:5]
    result = [
        {
            'title': recommendation[1],
            'url': url_for('article.article', title=recommendation[1]),
            'price': recommendation[0]
        } for recommendation in recommendations
    ]
    return jsonify(result)
