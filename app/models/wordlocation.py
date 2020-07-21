from app.models import db


class WordLocation(db.Model):
    __tablename__ = 'wordlocation'

    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.Integer)

    # ForeignKey
    # backref='word'
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'))
    # backref='article'
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))

    @classmethod
    def clear(cls):
        """清除所有索引"""
        for wordlocation in cls.query.all():
            db.session.delete(wordlocation)
        db.session.commit()

    def __repr__(self):
        return f"<WordLocation {self.article.title} {self.word.value} {self.location}>"
