from app import logger
from app.models import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    # relationship
    articles = db.relationship('Article', backref='category', lazy='dynamic')

    __mapper_args__ = {"order_by": name}

    @classmethod
    def insert_categores(cls):
        category_names = ['Algorithm', 'Tool', 'Program', 'Manual', 'System', 'Network']
        for category_name in category_names:
            category = cls.query.filter_by(name=category_name).first()
            if category is None:
                logger.info('Category: add %s' % category_name)
                category = cls(name=category_name)
            db.session.add(category)
        db.session.commit()
        logger.info('Insert categores is done.')

    @classmethod
    def clear(cls):
        """清理size小于等于0的标签"""
        for category in cls.query.all():
            if category.articles is None:
                db.session.delete(category)
        db.session.commit()

    def __repr__(self):
        return '<Category %r>' % self.name
