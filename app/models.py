import os
import hashlib

from app import db
from config import Config

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r - %s>' % (self.username, self.role.name)

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
        """判断md文件是否改变，是则更新记录, 并返回True"""
        old_md5 = self.md5
        now_md5 = self._get_md5()
        if old_md5 != now_md5:
            self.md5 = now_md5
            return True
        else:
            return False

    @classmethod
    def refresh(cls):

        # 存在文件的name集合
        existed_articles = set()
        for md_name in os.listdir(Config.ARTICLES_SOURCE_DIR):
            existed_articles.add(md_name.split('.')[0])

        # 已记录文件的name集合
        loged_articles = {article.name for article in cls.query.all()}

        # 有记录却不存在的文件
        for name in loged_articles - existed_articles:
            db.session.delete(cls.query.filter_by(name=name).first())

        # 存在却没有记录的文件
        for name in existed_articles - loged_articles:
            article = cls(name=name)
            article.md5 = article._get_md5()
            db.session.add(article)

        db.session.commit()
