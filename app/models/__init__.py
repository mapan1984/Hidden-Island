from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User, AnonymousUser
from app.models.category import Category
from app.models.tag import Tag
belong_to = db.Table(
    'belong_to',
    db.Column('tag_id', db.Integer,
              db.ForeignKey('tags.id'),
              primary_key=True),
    db.Column('article_id', db.Integer,
              db.ForeignKey('articles.id'),
              primary_key=True)
)
from app.models.words import Words
from app.models.wordlocation import WordLocation
from app.models.article import Article
from app.models.comment import Comment
from app.models.rating import Rating


__all__ = [
    db,
    Permission, Role, User, AnonymousUser,
    Category, Tag,
    belong_to,
    Words,
    Article,
    Comment, Rating,
    WordLocation,
]
