import os
from datetime import datetime

from flask import current_app, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired

from app import login_manager, logger
from app.models import db, Permission, Role


from flask_login import UserMixin, AnonymousUserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))    # 真实姓名
    username = db.Column(db.String(64), unique=True)  # 用户名
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    # relationship
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    articles = db.relationship('Article', backref='author', lazy='dynamic')
    ratings = db.relationship('Rating', backref='user', lazy='dynamic')

    # ForeignKey
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, **kwargs):
        """
        为使用管理员邮件地址进行注册的用户分配管理员的角色；
        否则，注册的默认角色为 `User`(default=True)
        """
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN_EMAIL']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def can(self, permissions):
        return (self.role is not None
                and (self.role.permissions & permissions) == permissions)

    @property
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @classmethod
    def add_admin(cls):
        email = os.environ.get('ADMIN_EMAIL')
        if email is None:
            logger.error('ADMIN_EMAIL not find in os.environ')
            return

        admin = cls.query.filter_by(email=email).first()
        if admin is None:
            logger.info('User: add admin')
            password = os.environ.get('ADMIN_PASSWORD')
            if password is None:
                logger.error('ADMIN_PASSWORD not find in os.environ')
                return
            admin = cls(
                username='mapan1984',
                email=email,
                password=password,
                confirmed=True,
            )
            db.session.add(admin)
            db.session.commit()
            logger.info('Add admin is done.')
        else:
            logger.info('Admin already exists.')

    def ping(self):
        """刷新用户的最后访问时间"""
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_password_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_change_email_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def generate_auth_token(self, expiration):
        """为api生成用户认证token"""
        s = Serializer(
            current_app.config['SECRET_KEY'],
            expires_in=expiration
        )
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        """
        为api验证用户token

        Args:
            token: 客户端请求的token字段

        Returns:
            token错误则返回None，否则返回对应用户(可能为None)
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return None
        return User.query.get(data['id'])

    def to_json(self):
        user_json = {
            'url': url_for('api.get_user', id=self.id, _external=True),
            'username': self.username,
            'email': self.email,
        }
        return user_json

    def __repr__(self):
        return '<User %r - %s>' % (self.username, self.role.name)


class AnonymousUser(AnonymousUserMixin):
    """
    为保持一致，为未登录用户实现`can`与`is_administrator`方法
    """

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.request_loader
def load_user_from_request(request):
    user = None
    if request.authorization:
        email_or_token = request.authorization.username
        password = request.authorization.password
        if email_or_token == '':  # 匿名用户
            user = AnonymousUser()
        elif password == '':  # 使用token验证
            user = User.verify_auth_token(email_or_token)
            if user is not None:
                user._token_used = True
                logger.info(f'{user.email} login in by token')
        else:  # 使用email和password验证
            user = User.query.filter_by(email=email_or_token).first()
            if user:
                if user.verify_password(password):
                    logger.info(f'{user.email} login in by password')
                else:
                    user = None

    return user
