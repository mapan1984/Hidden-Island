import os
import os.path
import hashlib
import bleach
import markdown
from datetime import datetime
from itertools import groupby

import jieba
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin

from app import db, redis, login_manager
from config import Config
from app.utils.markdown import MD
from app.utils.similarity import similarity
from app.utils.convert import todatetime
from app.utils.similarity import should_ignore
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
                print('Role: add %s' % role_name)
                role = cls(name=role_name)
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
            print('ADMIN_EMAIL not find in os.environ')
            return

        admin = cls.query.filter_by(email=email).first()
        if admin is None:
            print('User: add admin')
            password = os.environ.get('ADMIN_PASSWORD')
            if password is None:
                print('ADMIN_PASSWORD not find in os.environ')
                return
            admin = cls(
                username='mapan1984',
                email=email,
                password=password,
                confirmed=True,
            )
            db.session.add(admin)
            db.session.commit()
            print('Add admin is done.')
        else:
            print('Admin already exists.')

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


# Flask_Login要求的加载用户的回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##### Articles
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
                print('Category: add %s' % category_name)
                category = cls(name=category_name)
            db.session.add(category)
        db.session.commit()
        print('Insert categores is done.')

    @classmethod
    def clear(cls):
        """清理size小于等于0的标签"""
        for category in cls.query.all():
            if category.articles is None:
                db.session.delete(category)
        db.session.commit()

    def __repr__(self):
        return '<Category %r>' % self.name


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
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    md5 = db.Column(db.String(32))

    # Relationship
    tags = db.relationship(
        'Tag',
        secondary=belong_to,
        backref=db.backref('articles', lazy='dynamic'),
        lazy='dynamic',
    )
    comments = db.relationship('Comment', backref='article', lazy='dynamic')
    ratings = db.relationship('Rating', backref='article', lazy='dynamic')
    wordlocations = db.relationship('WordLocation', backref='article', lazy='dynamic')

    # ForeignKey
    # backref='category'
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    # backref='author'
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    __mapper_args__ = {"order_by": desc(timestamp)}

    @classmethod
    def archives(cls):
        archives = groupby(
            cls.query.all(),
            key=lambda article: (article.timestamp.year, article.timestamp.month)
        )
        return archives

    @property
    def content(self):
        """整合标题、分类、标签等内容并返回，用于文章的相似性判断"""
        content = " ".join([self.body]
                           + [self.title] * 3
                           + [self.category.name] * 3
                           + [tag.name for tag in self.tags] * 3)
        return content

    @property
    def words(self):
        """对自身的markdown格式内容进行中文分词并返回结果"""
        words = [word.lower() for word in jieba.cut_for_search(self.content)]
        return words

    def _is_indexed(self):
        """如果文章已经在WordLocation中建立索引，则返回True"""
        return WordLocation.query.filter_by(article=self).first() is not None

    def _build_index(self):
        """为文章建立索引"""
        if self._is_indexed():
            return
        print('Indexing %s' % self.title)

        for loc, word_value in enumerate(self.words):
            if Words._should_ignore(word_value):
                continue
            word = Words.query.filter_by(value=word_value).first()
            if word is None:
                word = Words(value=word_value)
                db.session.add(word)
                db.session.commit()
            wordlocation = WordLocation(article=self, word=word, location=loc)
            db.session.add(wordlocation)
            db.session.commit()

    def _del_index(self):
        """删除文章索引"""
        if self.wordlocations:
            for wordlocation in self.wordlocations:
                db.session.delete(wordlocation)
            db.session.commit()

    def _rebuild_index(self):
        """重新为文章建立索引"""
        self._del_index()
        self._build_index()

    def _cache_similar(self):
        print(f"Cache {self.name}")
        for other in Article.query.all():
            if self == other:
                continue
            similar = similarity(self.content, other.content)
            redis.zadd(self.name, similar, other.name)
            redis.zadd(other.name, similar, other.name)

    def _delete_cache(self):
        redis.delete(self.name)
        for other in Article.query.all():
            if self == other:
                continue
            redis.zdelete(other.name, self.name)

    def add_tags(self, tag_names):
        """增加文章的tags
        Args:
            tag_names: tag名称组成的list
        """
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag is None:
                tag = Tag(name=tag_name)
            db.session.add(tag)
            self.tags.append(tag)

    def delete_tags(self):
        """删除文章的所有tag"""
        for tag in self.tags.all():
            self.tags.remove(tag)
            if tag.articles is None:
                db.session.delete(tag)

    def change_category(self, category):
        """改变文章的category(如果之前不存在category则增加)
        Args:
            category: category的名称或id
        """
        if isinstance(category, int):
            new_category = Category.query.get(category)
            self.category = new_category
            return
        new_category = Category.query.filter_by(name=category).first()
        if new_category is None:
            new_category = Category(name=category)
        self.category = new_category

    def delete(self):
        """删除存在的文章记录"""
        self.delete_tags()
        # XXX: 后台执行
        self._del_index()
        self._delete_cache()
        db.session.delete(self)
        return "[article] %s is deleted" % self.title

    def get_md5(self):
        """得到文章的md5值"""
        md5 = hashlib.md5()
        with open(self.sc_path, "rb") as scf:
            while True:
                content = scf.read(1024)
                if not content:
                    break
                md5.update(content)
        return md5.hexdigest()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        target.body_html = MD.convert(value)
        # TODO: 为新增文章建立index
        # NOTE: 要注意文章内容改变则立即执行，
        #       而此时可能文章还没有id(要db.commit后)，
        #       并且文章的标题、目录和标签可能未改变
        # rebuild_index.delay(target)

    def to_json(self):
        """将文章信息转换为json格式"""
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
        title = json_article.get('title')
        if title is None or title == '':
            raise ValidationError('Article does not have title')
        body = json_article.get('body')
        if body is None or body == '':
            raise ValidationError('Article does not have body')
        category = json_article.get('category', '未分类')
        tags = json_article.get('tags', '无标签')
        # TODO: 如果文章title(name)重复应进行提示
        article = Article(
            title=title,
            name=title,
            body=body,
        )
        article.change_category(category)
        article.add_tags(tags)
        return article

    @staticmethod
    def from_jekyll_json(json_article):
        """同步jekyll文章"""
        article_file_name = json_article.get('article_file_name')
        category_name = json_article.get('category_name')

        content = json_article.get('content')
        if content is None or content == '':
            raise ValidationError('Article does not have a body ')

        article = Article()
        article.body = content  # 必须
        article.body_html = MD.convert(content)
        title = MD.Meta.get('title')  # 必须
        if title is None or title == '':
            raise ValidationError('Article does not have title')
        article.title = title
        article.name = article.title  # 必须

        timestamp = MD.Meta.get('date')  # 优先文件头定义的date
        if timestamp:
            article.timestamp = todatetime(timestamp)
        else:  # 否则试图从文件名提取date
            article.timestamp = todatetime(article_file_name)

        tag_names = MD.Meta.get('tags', ['无标签'])

        try:
            article.change_category(category_name)
            article.add_tags(tag_names)
            db.session.add(article)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return None
        else:
            return article

    def __repr__(self):
        return '<Article %r>' % self.name

    # The following function are ready for the markdwon file
    @property
    def md_name(self):
        return self.name + '.md'

    @property
    def sc_path(self):
        return os.path.join(Config.ARTICLES_SOURCE_DIR, self.md_name)

    def md_is_change(self):
        old_md5 = self.md5
        now_md5 = self.get_md5()
        return old_md5 != now_md5

    def md_relog(self):
        """对`/articles`目录中已经记录的文章，重新记录文章中各属性"""
        with open(self.sc_path, "r", encoding="utf-8") as scfd:
            self.body = scfd.read()

        self.body_html = MD.convert(self.body)
        title = MD.Meta.get('title')  # 必须
        if title is None or title == '':
            raise ValidationError('Article does not have title')
        self.title = title

        timestamp = MD.Meta.get('date')
        if timestamp:
            self.timestamp = todatetime(timestamp)
        else:  # 否则试图从文件名提取date
            self.timestamp = todatetime(self.name)

        self.md5 = self.get_md5()

        admin_role = Role.query.filter_by(name='Administrator').first()
        self.author = User.query.filter_by(role=admin_role).first()

        category_name = MD.Meta.get('category', '未分类')
        tag_names = MD.Meta.get('tags', ['无标签'])

        try:
            self.change_category(category_name)
            self.delete_tags()
            self.add_tags(tag_names)
            db.session.add(self)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return None
        else:
            return self

    @classmethod
    def md_render(cls, name):
        """根据markdown文件生成文章记录，更新记录中各属性
        Args:
            name: 文件名(去除后缀)
        """
        try:
            article = Article(name=name).md_relog()
        except ValidationError as exp:
            return "Error when render %s: %s" % (name, str(exp))
        else:
            if not article:
                return "Message: may be %s exsited." % name
            # XXX: 后台执行
            article._build_index()
            article._cache_similar()
            return "[article] %s is added." % name

    @staticmethod
    def md_delete(name):
        """删除markdown文件
        Args:
            name: markdown文件名
        """
        sc_path = os.path.join(Config.ARTICLES_SOURCE_DIR, name + '.md')
        if os.path.isfile(sc_path):
            os.remove(sc_path)
            return "[markdown file] %s is deleted." % name

    def md_refresh(self):
        """更新存在的由markdown文件生成的article的记录"""
        self.md_relog()
        # XXX: 后台执行
        self._rebuild_index()
        self._cache_similar()
        return "[article] %s is refreshed" % self.title

    @classmethod
    def md_render_all(cls):
        """记录未曾被记录的markdown文件"""
        # 获取存在的markdown文件的name集合
        existed_md_articles = {md_name.split('.')[0] for md_name in os.listdir(Config.ARTICLES_SOURCE_DIR)}

        # 获取管理员的已记录文件的name集合
        admin_role = Role.query.filter_by(name='Administrator').first()
        admin_user = User.query.filter_by(role=admin_role).first()
        loged_articles = {article.name for article in cls.query.filter_by(author=admin_user).all()}

        # 增加(存在markdown文件却没有记录)的文件记录
        for name in existed_md_articles - loged_articles:
            cls.md_render(name)

    @classmethod
    def md_refresh_all(cls):
        """查看是否有文件改变，改变则更新markdown文件记录"""
        # 获取存在的markdown文件的name集合
        existed_md_articles = {md_name.split('.')[0] for md_name in os.listdir(Config.ARTICLES_SOURCE_DIR)}

        # 获取管理员的已记录文件实例集合
        admin_role = Role.query.filter_by(name='Administrator').first()
        admin_user = User.query.filter_by(role=admin_role).first()
        loged_md_articles = {article for article in cls.query.filter_by(author=admin_user).all() if article.name in existed_md_articles}

        for article in loged_md_articles:
            if article.md_is_change():
                article.md_refresh()


db.event.listen(Article.body, 'set', Article.on_changed_body)


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
            'id': self.id,
            'body': self.body,
            'author': self.author.username,
            'timestamp': self.timestamp.strftime('%Y %m %d'),
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
            raise ValidationError('Comment does not have a body')
        return Comment(body=body, author_id=author_id, article_id=article_id)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b',
                        'code', 'em', 'i', 'strong']
        target.body_html = bleach.linkify(
            bleach.clean(
                markdown.markdown(value, output_format='html'),
                tags=allowed_tags,
                strip=True
            )
        )

    def __repr__(self):
        return ('<Comment of %r for %r>'
                % (self.author.username, self.article.title))


db.event.listen(Comment.body, 'set', Comment.on_changed_body)


class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.SmallInteger)

    # ForeignKey
    # backref=user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # backref=article
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))

    def __repr__(self):
        return ('<Rating of %r for %r>'
                % (self.user.username, self.article.title))


class Words(db.Model):
    __tablename__ = 'words'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(64), unique=True, index=True)

    # Relationship
    wordlocations = db.relationship('WordLocation', backref='word', lazy='dynamic')

    @staticmethod
    def _should_ignore(word):
        return should_ignore(word)

    @classmethod
    def clear(cls):
        """清除所有索引"""
        for word in cls.query.all():
            db.session.delete(word)
        db.session.commit()

    def __repr__(self):
        return "<Word %s>" % self.value


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
