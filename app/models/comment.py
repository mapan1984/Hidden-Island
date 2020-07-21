from datetime import datetime

import bleach
import markdown
from flask import url_for

from app.exceptions import ValidationError
from app.models import db


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True,
                          default=datetime.utcnow)
    disabled = db.Column(db.Boolean)

    # ForeignKey
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))

    # __mapper_args__ = {"order_by": desc(timestamp)}

    def to_json(self):
        comments = {
            'url': url_for('api.get_comment', id=self.id, _external=True),
            'id': self.id,
            'body': self.body,
            'body_html': self.body_html,
            'author': self.author.username,
            'timestamp': self.timestamp.strftime('%Y %m %d'),
            'author_id': self.author_id,
            'article_id': self.article_id,
        }
        return comments

    @staticmethod
    def from_json(comment):
        """根据客户端提交的json创建评论"""
        body = comment.get('body')
        author_id = comment.get('author_id')
        article_id = comment.get('article_id')
        if body is None or body == '':
            raise ValidationError('Comment does not have a body')
        return Comment(body=body, author_id=author_id, article_id=article_id)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b',
                        'code', 'em', 'i', 'strong']
        target.body_html = bleach.linkify(
            bleach.clean(
                markdown.markdown(value, output_format='html'),
                tags=allowed_tags,
                strip=True
            )
        )

    def __repr__(self):
        return ('<Comment of %r for %r>'
                % (self.author.username, self.article.title))


db.event.listen(Comment.body, 'set', Comment.on_changed_body)

