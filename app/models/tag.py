from app.models import db


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    __mapper_args__ = {"order_by": name}

    @classmethod
    def clear(cls):
        """清理size小于等于0的标签"""
        for tag in cls.query.all():
            if tag.articles is None:
                db.session.delete(tag)
        db.session.commit()

    def __repr__(self):
        return '<Tag %r>' % self.name

