from app.models import db


class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.SmallInteger)

    # ForeignKey
    # backref=user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # backref=article
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))

    def __repr__(self):
        return ('<Rating of %r for %r>'
                % (self.user.username, self.article.title))

