import os
import os.path
import hashlib
import bleach
import markdown
from datetime import datetime

from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin

from app import db, login_manager
from config import Config
from app.misc import MD, convert_date
from app.exceptions import ValidationError


##### Auth
class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    # relationship
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW | Permission.COMMENT, True),
            'Author': (Permission.FOLLOW
                       | Permission.COMMENT
                       | Permission.WRITE_ARTICLES
                       | Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for role_name in roles.keys():
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                print('Role: add %s' % role_name)
                role = Role(name=role_name)
            role.permissions = roles[role_name][0]
            role.default = roles[role_name][1]
            db.session.add(role)
        db.session.commit()
        print('Insert roles is done.')

    def __repr__(self):
        return '<Role %r>' % self.name


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
                self.role = Role.query.filter_by(permissions=0xff).frist()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def can(self, permissions):
        return self.role is not None \
               and (self.role.permissions & permissions) == permissions

    @property
    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @staticmethod
    def add_admin():
        email = os.environ.get('ADMIN_EMAIL')
        if email is None:
            print('ADMIN_EMAIL not find in os.environ')
            return
        user = User.query.filter_by(email=email).first()
        if user is None:
            print('User: add admin')
            user = User(email=email,
                        username='admin',
                        password=os.environ.get('ADMIN_PASSWORD'),
                        confirmed=True,
                        role=Role.query.filter_by(permissions=0xff).first())
            db.session.add(user)
            db.session.commit()
        print('Add admin is done.')

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
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_password_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
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
        except:
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


# Flask_Login要求的加载用户的回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##### Articles
class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    size = db.Column(db.Integer, default=0)

    # relationship
    articles = db.relationship('Article', backref='category', lazy='dynamic')

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


belong_to = db.Table(
    'belong_to',
    db.Column('tag_id', db.Integer,
              db.ForeignKey('tags.id'),
              primary_key=True),
    db.Column('article_id', db.Integer,
              db.ForeignKey('articles.id'),
              primary_key=True)
)


class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)  # 文件名或标题
    title = db.Column(db.String(64), unique=True)  # 标题
    datestr = db.Column(db.String(64))
    date = db.Column(db.Date)
    timestamp = db.Column(db.DateTime, index=True,
                          default=datetime.utcnow)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    md5 = db.Column(db.String(32))

    # relationship
    tags = db.relationship('Tag',
                           secondary=belong_to,
                           backref=db.backref('articles', lazy='dynamic'),
                           lazy='dynamic')
    comments = db.relationship('Comment', backref='article', lazy='dynamic')
    ratings = db.relationship('Rating', backref='article', lazy='dynamic')

    # ForeignKey
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    __mapper_args__ = {"order_by": desc(timestamp)}

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
        """删除文章的所有tag"""
        for tag in self.tags.all():
            tag.size -= 1
            self.tags.remove(tag)
            if tag.size == 0:
                db.session.delete(tag)

    def change_category(self, category):
        """改变文章的category(如果之前不存在category则增加)"""
        old_category = self.category
        if isinstance(category, str):
            new_category = Category.query.filter_by(name=category).first()
        else:
            new_category = category

        if old_category is not None and new_category == old_category:
            return None

        if new_category is None:
            new_category = Category(name=category, size=0)

        if old_category is not None:
            old_category.size -= 1
            if old_category.size == 0:
                db.session.delete(old_category)

        new_category.size += 1
        db.session.add(new_category)
        self.category = new_category

    def delete(self):
        """删除存在的文章记录"""
        self.delete_tags()
        self.category.size -= 1
        if self.category.size == 0:
            db.session.delete(self.category)
        db.session.delete(self)
        return "[article] %s is deleted" % self.title

    def get_md5(self):
        md5 = hashlib.md5()
        with open(self.sc_path, "rb") as scf:
            while True:
                content = scf.read(1024)
                if not content:
                    break
                md5.update(content)
        return md5.hexdigest()

    @staticmethod
    def on_change_body(target, value, oldvalue, initiator):
        target.body_html = MD.convert(value)

    def to_json(self):
        article_json = {
            'url': url_for('api.get_article', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author_url': url_for('api.get_user', id=self.author_id),
        }
        return article_json

    @staticmethod
    def from_json(json_article):
        """根据客户端提交的json创建博客文章"""
        body = json_article.get('body')
        if body is None or body == '':
            raise ValidationError('article does not have a body')
        return Article(body=body)

    def __repr__(self):
        return '<Article %r>' % self.name

    # the following function are ready for the markdwon file
    @property
    def md_name(self):
        return self.name+'.md'

    @property
    def sc_path(self):
        return os.path.join(Config.ARTICLES_SOURCE_DIR, self.md_name)

    def md_is_change(self):
        old_md5 = self.md5
        now_md5 = self.get_md5()
        if old_md5 != now_md5:
            return True
        else:
            return False

    def md_relog(self):
        """`/articles`目录中的文章，文章记录已存在，更新文章记录中各属性"""
        with open(self.sc_path, "r", encoding="utf-8") as scfd:
            self.body = scfd.read()
            self.body_html = MD.convert(self.body)

        self.title   = MD.Meta.get('title', [''])[0]
        self.datestr = MD.Meta.get('date', [''])[0]
        self.date    = convert_date(self.datestr)
        self.md5     = self.get_md5()
        admin_role = Role.query.filter_by(permissions=0xff).first()
        self.author  = User.query.filter_by(role=admin_role).first()

        category_name = MD.Meta.get('category', [''])[0]
        self.change_category(category_name)

        tag_names     = MD.Meta.get('tag')
        self.delete_tags()
        self.add_tags(tag_names)

    @classmethod
    def md_render(cls, name):
        """根据md文件生成文章记录，更新记录中各属性
        name: 文件名(去除后缀)
        """
        article = Article(name=name)
        article.md_relog()
        db.session.add(article)
        return "[article] %s is added" % name

    @staticmethod
    def md_delete(name):
        """删除存在文章记录的md文件"""
        sc_path = os.path.join(Config.ARTICLES_SOURCE_DIR, name+'.md')
        if os.path.isfile(sc_path):
            os.remove(sc_path)
            return "[md] %s is deleted." % name

    def md_refresh(self):
        """更新存在的article记录"""
        self.md_relog()
        return "[article] %s is refreshed" % self.title

    @classmethod
    def md_render_all(cls):
        """根据md文件生成html文件"""
        # 获取存在的md文件的name集合
        existed_md_articles = set()
        for md_name in os.listdir(Config.ARTICLES_SOURCE_DIR):
            existed_md_articles.add(md_name.split('.')[0])

        # 获取已记录文件的name集合
        loged_articles = {article.name for article in cls.query.all()}

        # 增加(存在md文件却没有记录)的文件记录，并生成html文件
        for name in existed_md_articles - loged_articles:
            cls.md_render(name)

    @classmethod
    def md_refresh_all(cls):
        """查看是否有文件改变，改变则更新html文件和数据库记录"""
        for article in cls.query.all():
            if article.md_is_change():
                article.md_refresh()


db.event.listen(Article.body, 'set', Article.on_change_body)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True,
                          default=datetime.utcnow)
    disabled = db.Column(db.Boolean)

    # ForeignKey
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))

    __mapper_args__ = {"order_by": desc(timestamp)}

    def to_json(self):
        comments = {
            'body': self.body,
            'author': self.author.username,
            'timestamp': self.timestamp,
            'author_id': self.author_id,
            'article_id': self.article_id,
        }
        return comments

    @staticmethod
    def from_json(comment):
        """根据客户端提交的json创建评论"""
        body = comment.get('body')
        author_id = comment.get('author_id')
        article_id = comment.get('article_id')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(body=body, author_id=author_id, article_id=article_id)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b',
                        'code', 'em', 'i', 'strong']
        target.body_html = bleach.linkify(bleach.clean(
                markdown.markdown(value, output_format='html'),
                tags=allowed_tags, strip=True))

    def __repr__(self):
        return '<Comment of %r for %r>'\
                % (self.author.username, self.article.title)


db.event.listen(Comment.body, 'set', Comment.on_changed_body)


class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.SmallInteger)

    # ForeignKey
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))

    def __repr__(self):
        return '<Rating of %r for %r>'\
                % (self.user.username, self.article.title)
