""" 程序包的构造文件 """

import os

from flask import Flask, render_template, Blueprint
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

from config import Config

bootstrap = Bootstrap()
db = SQLAlchemy()

def mkdir(path):
    """ 根据path创建目录 """
    if not os.path.exists(path):
        os.makedirs(path)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)

    mkdir(app.config['ARTICLES_DESTINATION_DIR'])
    mkdir(app.config['ARTICLES_SOURCE_DIR'])

    app_ctx = app.app_context()
    app_ctx.push()
    from app.article_log import ArticleLog
    app_ctx.pop()

    app.config['LOG'] = ArticleLog(app.config['ARTICLES_SOURCE_DIR'])

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .article import article as article_blueprint
    app.register_blueprint(article_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint)

    return app
