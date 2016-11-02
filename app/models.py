import os
import hashlib

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db, login_manager
from config import Config
from app.generate import generate_article

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r - %s>' % (self.username, self.role.name)


# Flask_Login要求的加载用户的回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    md5 = db.Column(db.String(64), unique=True)
    name = db.Column(db.String(64), unique=True)

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

    def _get_md5(self):
        """返回文件md5值"""
        if not os.path.isfile(self.sc_path):
            print("%s is not a file" % self.sc_path)
        md5 = hashlib.md5()
        with open(self.sc_path, "rb") as fd:
            while True:
                content = fd.read(1024)
                if not content:
                    break
                md5.update(content)
        return md5.hexdigest()

    def is_change(self):
        """判断md文件是否改变，是则(更新记录), 并返回True"""
        old_md5 = self.md5
        now_md5 = self._get_md5()
        if old_md5 != now_md5:
            return True
        else:
            return False

    @classmethod
    def refresh(cls):
        """更新数据库记录"""

        # 存在的文件的name集合
        existed_articles = set()
        for md_name in os.listdir(Config.ARTICLES_SOURCE_DIR):
            existed_articles.add(md_name.split('.')[0])

        # 已记录文件的name集合
        loged_articles = {article.name for article in cls.query.all()}

        # 删除(有记录却不存在的文件)的文件记录
        for name in loged_articles - existed_articles:
            print("%s is deleted" % name)
            db.session.delete(cls.query.filter_by(name=name).first())

        # 增加(并生成)(存在却没有记录的文件)的文件记录
        for name in existed_articles - loged_articles:
            print("%s is added" % name)
            article = Article(name=name)
            article.md5 = article._get_md5()
            db.session.add(article)
            generate_article(article.sc_path, article.ds_path)

        # 查看是否有文件改变，改变则更新html文件和数据库记录
        for article in cls.query.all():
            if article.is_change():
                print("%s is changed" % article.md_name)
                article.md5 = article._get_md5()
                db.session.add(article)
                generate_article(article.sc_path, article.ds_path)
            else:
                print("%s is existed and %s is not changed"
                      % (article.html_name, article.md_name))

        db.session.commit()

    def __repr__(self):
        return '<Article %r>' % self.name
