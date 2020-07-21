import os
import hashlib
from itertools import groupby
from datetime import datetime

import jieba
from flask import url_for
from sqlalchemy import desc

from app import redis, logger
from config import Config
from app.utils.markdown import MD
from app.utils.convert import todatetime
from app.utils.similarity import similarity
from app.exceptions import ValidationError
from app.models import db, belong_to, User, Role, Words, WordLocation, Tag, Category


class Article(db.Model):
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True)  # 标题
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)

    # For markdown file
    name = db.Column(db.String(64), unique=True, index=True)  # 文件名(可能为标题)
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
        logger.info(f'Indexing {self.title}...')

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

    def _delete_index(self):
        """删除文章索引"""
        if self.wordlocations:
            for wordlocation in self.wordlocations:
                db.session.delete(wordlocation)
            db.session.commit()

    def _rebuild_index(self):
        """重新为文章建立索引"""
        self._delete_index()
        self._build_index()

    def _cache_similar(self):
        logger.info(f"Cache: {self.title}")
        for other in Article.query.all():
            if self == other:
                continue
            sim = similarity(self.content, other.content)
            redis.zadd(self.title, {other.title: sim})
            redis.zadd(other.title, {self.title: sim})

    def _delete_cache(self):
        logger.info(f"Delete Cache: {self.title}")
        redis.delete(self.title)
        for other in Article.query.all():
            if self == other:
                continue
            redis.zrem(other.title, self.title)

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

    def set_category(self, category):
        """设置文章的category(如果之前不存在category则增加)
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
        self._delete_index()
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
        tags = json_article.get('tags', ['无标签'])
        # TODO: 如果文章title(name)重复应进行提示
        article = Article(
            title=title,
            name=title,
            body=body,
        )
        article.set_category(category)
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
            # XXX: 查清标题冲突发生在那一步
            article.set_category(category_name)
            article.add_tags(tag_names)
            db.session.add(article)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return None
        else:
            return article

    def __repr__(self):
        return '<Article %r>' % self.title

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
            self.set_category(category_name)
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
            from app.tasks import build_index
            build_index.delay(article.id)
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
        from app.tasks import rebuild_index
        rebuild_index.delay(self.id)
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
