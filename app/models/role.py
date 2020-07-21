from app import logger
from app.models import db, Permission


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    # relationship
    users = db.relationship('User', backref='role', lazy='dynamic')

    @classmethod
    def insert_roles(cls):
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT, True),
            'Author': (Permission.FOLLOW
                       | Permission.COMMENT
                       | Permission.WRITE_ARTICLES
                       | Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for role_name in roles.keys():
            role = cls.query.filter_by(name=role_name).first()
            if role is None:
                logger.info('Role: add %s' % role_name)
                role = cls(name=role_name)
            role.permissions = roles[role_name][0]
            role.default = roles[role_name][1]
            db.session.add(role)
        db.session.commit()
        logger.info('Insert roles is done.')

    def __repr__(self):
        return '<Role %r>' % self.name
