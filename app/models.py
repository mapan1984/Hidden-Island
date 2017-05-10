import os
import os.path
import hashlib
import markdown
import bleach
import datetime

from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, render_template
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
    comments = db.relationship('Comment', backref='author', lazy='dynamic')

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
                        confirmed=True,
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
    size = db.Column(db.Integer, default=0)

    __mapper_args__ = {"order_by": desc(size)}

    @classmethod
    def clear(cls):
        """清理size小于等于0的目录"""
        for category in cls.query.all():
            if category.size <= 0:
                db.session.delete(category)
        db.session.commit()

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
    size = db.Column(db.Integer, default=0)

    __mapper_args__ = {"order_by": desc(size)}

    @classmethod
    def clear(cls):
        """清理size小于等于0的标签"""
        for tag in cls.query.all():
            if tag.size <= 0:
                db.session.delete(tag)
        db.session.commit()

    def __repr__(self):
        return '<Tag %r>' % self.name


MONTH_MAP = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}

# Thu Apr 27 21:24:32 CST 2017 --> 2017-4-27
def convert_date(date):
    _, month, day, _, _, year = date.split(' ')
    month = MONTH_MAP[month]
    return datetime.date(int(year), month, int(day))

# markdown
MD = markdown.Markdown(
    extensions=[
        "markdown.extensions.codehilite(css_class=highlight,linenums=None)",
        "markdown.extensions.meta",
        "markdown.extensions.tables",
        "markdown.extensions.toc",
    ]
)

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    title = db.Column(db.String(64), unique=True)
    datestr = db.Column(db.String(64))
    date = db.Column(db.Date)
    body = db.Column(db.Text)
    md5 = db.Column(db.String(32))
    tags = db.relationship('Tag',
                           secondary=belong_to,
                           backref=db.backref('articles', lazy='dynamic'),
                           lazy='dynamic')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    comments = db.relationship('Comment', backref='article', lazy='dynamic')

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

    def add_tags(self, tag_names):
        """增加文章的tags
        tag_names: tag名字组成的list
        """
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag is None:
                tag = Tag(name=tag_name, size=0)
            tag.size += 1
            db.session.add(tag)
            self.tags.append(tag)

    def delete_tags(self):
        """删除文章的tags"""
        for tag in self.tags.all():
            tag.size -= 1
            self.tags.remove(tag)
            if tag.size == 0:
                db.session.delete(tag)

    def change_category(self, category_name):
        """该变文章的category(如果之前不存在category则增加)"""
        new_category = Category.query.filter_by(name=category_name).first()
        if new_category is None:
            category = Category(name=category_name, size=0)
            category.size += 1
            db.session.add(category)
            self.category = category
            return None
        old_category = self.category
        if old_category is None:
            new_category.size += 1
            db.session.add(new_category)
            self.category = new_category
            return None
        elif old_category != new_category:
            old_category.size -= 1
            if old_category.size == 0:
                de.session.delete(old_category)
            db.session.add(old_category)

            new_category.size += 1
            db.session.add(new_category)
            self.category = new_category

    def generate_article(self):
        with open(self.sc_path, "r", encoding="utf-8") as scfd:
            content = MD.convert(scfd.read())

        title         = MD.Meta.get('title')[0]
        datestr       = MD.Meta.get('date')[0]
        date          = convert_date(datestr)
        category_name = MD.Meta.get('category')[0]
        tag_names     = MD.Meta.get('tag')

        destination_html = render_template('_layouts/content.html',
                                           name=self.name,
                                           title=title,
                                           datestr=datestr,
                                           category=category_name,
                                           tags=tag_names,
                                           content=content)

        self.title   = title
        self.body    = destination_html
        self.md5     = self.get_md5()
        self.datestr = datestr
        self.date    = date

        self.change_category(category_name)

        self.delete_tags()
        self.add_tags(tag_names)

    @classmethod
    def render(cls, name):
        """根据md文件生成html文件
        name: 文件名(去除后缀)
        """
        article = Article(name=name)
        article.generate_article()
        db.session.add(article)
        return "[article] %s is added" % name

    def refresh(self):
        """更新存在的article记录与html文件"""
        self.generate_article()
        return "[article] %s is refreshed" % self.title

    def delete_html(self):
        """删除存在的html文件与记录"""
        self.delete_tags()
        self.category.size -= 1
        if self.category.size == 0:
            db.session.delete(self.category)
        db.session.add(self.category)
        db.session.delete(self)
        return "[article] %s is deleted" % self.title

    def delete_md(self):
        sc_path = self.sc_path
        if os.path.isfile(sc_path):
            os.remove(sc_path)
            return "[md] %s.md is deleted" % self.name

    @classmethod
    def render_all(cls):
        """根据md文件生成html文件"""
        # 获取存在的md文件的name集合
        existed_md_articles = set()
        for md_name in os.listdir(Config.ARTICLES_SOURCE_DIR):
            existed_md_articles.add(md_name.split('.')[0])

        # 获取已记录文件的name集合
        loged_articles = {article.name for article in cls.query.all()}

        # 增加(存在md文件却没有记录)的文件记录，并生成html文件
        for name in existed_md_articles - loged_articles:
            cls.render(name)

    @classmethod
    def refresh_all(cls):
        """查看是否有文件改变，改变则更新html文件和数据库记录"""
        for article in cls.query.all():
            if article.is_change():
                article.refresh()

    def __repr__(self):
        return '<Article %r>' % self.name

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True,
                          default=datetime.datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))

    __mapper_args__ = {"order_by": desc(timestamp)}

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 
                        'code', 'em', 'i', 'strong']
        target.body_html = bleach.linkify(bleach.clean(
                markdown.markdown(value, output_format='html'),
                tags=allowed_tags, strip=True))

    def __repr__(self):
        return '<Comment of %r and %r>'\
                % (self.author.username, self.article.title)

db.event.listen(Comment.body, 'set', Comment.on_changed_body)
