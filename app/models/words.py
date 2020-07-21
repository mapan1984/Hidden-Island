from app.utils.similarity import should_ignore
from app.models import db


class Words(db.Model):
    __tablename__ = 'words'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(64), unique=True, index=True)

    # Relationship
    wordlocations = db.relationship('WordLocation', backref='word', lazy='dynamic')

    @staticmethod
    def _should_ignore(word):
        return should_ignore(word)

    @classmethod
    def clear(cls):
        """清除所有索引"""
        for word in cls.query.all():
            db.session.delete(word)
        db.session.commit()

    def __repr__(self):
        return "<Word %s>" % self.value

