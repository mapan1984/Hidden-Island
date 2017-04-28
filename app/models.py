import os
import os.path
import hashlib

from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin

from app import db, login_manager
from config import Config

##### Auth
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        role_names = ['User', 'Admin']
        for role_name in role_names:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                print('Role: add %s' % role_name)
                role = Role(name=role_name)
            db.session.add(role)
        db.session.commit()
        print('insert roles is done')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    @property
    def is_admin(self):
        return self.role.name == 'Admin'

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    @staticmethod
    def add_admin():
        email = os.environ.get('ADMIN_EMAIL')
        user = User.query.filter_by(email=email).first()
        if user is None:
            print('User: add admin')
            user = User(email=email,
                        username='admin',
                        password=os.environ.get('ADMIN_PASSWORD'),
                        role=Role.query.filter_by(name='Admin').first())
            db.session.add(user)
            db.session.commit()
        print('add admin is done')

    def __repr__(self):
        return '<User %r - %s>' % (self.username, self.role.name)


# Flask_Login要求的加载用户的回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##### Articles
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    articles = db.relationship('Article', backref='category', lazy='dynamic')

    @property
    def size(self):
        size = 0
        for _ in self.articles:
            size = size + 1
        return size

    def __repr__(self):
        return '<Category %r>' % self.name

belong_to = db.Table(
    'belong_to',
    db.Column('tag_id', db.Integer,
              db.ForeignKey('tags.id'),
              primary_key=True),
    db.Column('article_id', db.Integer,
              db.ForeignKey('articles.id'),
              primary_key=True)
)

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    @property
    def size(self):
        size = 0
        for _ in self.articles:
            size = size + 1
        return size

    def __repr__(self):
        return '<Tag %r>' % self.name

from app.generate import generate_article

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    title = db.Column(db.String(64), unique=True)
    datestr = db.Column(db.String(64))
    date = db.Column(db.Date)
    md5 = db.Column(db.String(32))
    tags = db.relationship('Tag',
                           secondary=belong_to,
                           backref=db.backref('articles', lazy='dynamic'),
                           lazy='dynamic')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    __mapper_args__ = {"order_by": desc(date)}

    @property
    def md_name(self):
        return self.name+'.md'

    @property
    def html_name(self):
        return self.name+'.html'

    @property
    def sc_path(self):
        return os.path.join(Config.ARTICLES_SOURCE_DIR, self.md_name)

    @property
    def ds_path(self):
        return os.path.join(Config.ARTICLES_DESTINATION_DIR, self.html_name)

    def get_md5(self):
        md5 = hashlib.md5()
        with open(self.sc_path, "rb") as scf:
            while True:
                content = scf.read(1024)
                if not content:
                    break
                md5.update(content)
        return md5.hexdigest()

    def is_change(self):
        old_md5 = self.md5
        now_md5 = self.get_md5()
        if old_md5 != now_md5:
            return True
        else:
            return False

    @classmethod
    def render(cls, name):
        article = Article(name=name)
        article.md5 = article.get_md5()
        db.session.add(article)
        generate_article(article)
        return "[article] %s is added" % name

    @classmethod
    def refresh(cls, name):
        article = cls.query.filter_by(name=name).first()
        article.md5 = article.get_md5()
        db.session.add(article)
        generate_article(article)
        return "[article] %s is refreshed" % name

    @classmethod
    def delete_html(cls, name):
        ds_path = os.path.join(Config.ARTICLES_DESTINATION_DIR, name+".html")
        if os.path.isfile(ds_path):
            os.remove(ds_path)
        article=cls.query.filter_by(name=name).first()
        for tag in article.tags.all():
            if tag.size == 1:
                db.session.delete(tag)
        if article.category.size == 1:
            db.session.delete(article.category)
        db.session.delete(article)
        return "%s.html is deleted" % name

    @classmethod
    def delete_md(cls, name):
        sc_path = os.path.join(Config.ARTICLES_SOURCE_DIR, name+".md")
        if os.path.isfile(sc_path):
            os.remove(sc_path)
            return "%s.md is deleted" % name

    @classmethod
    def refresh_all_articles(cls):
        """更新数据库记录"""
        # 获取存在的md文件的name集合
        existed_md_articles = set()
        for md_name in os.listdir(Config.ARTICLES_SOURCE_DIR):
            existed_md_articles.add(md_name.split('.')[0])

        # 获取已记录文件的name集合
        loged_articles = {article.name for article in cls.query.all()}

        # 增加(存在md文件却没有记录)的文件记录，并生成html文件
        for name in existed_md_articles - loged_articles:
            cls.render(name)

        # 删除(有记录却不存在md文件)的文件记录与生成的html文件
        for name in loged_articles - existed_md_articles:
            cls.delete_html(name)

        # 查看是否有文件改变，改变则更新html文件和数据库记录
        for article in cls.query.all():
            if article.is_change():
                cls.refresh(article)

    def __repr__(self):
        return '<Article %r>' % self.name
