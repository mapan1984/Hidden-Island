""" 程序包的构造文件 """

from flask import Flask, render_template, Blueprint
from flask_bootstrap import Bootstrap

from config import config
from app.file_monitor import FileMonitor

bootstrap = Bootstrap()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    config.init_app(app)

    bootstrap.init_app(app)

    app.config['MONITOR'] = FileMonitor(app.config['ARTICLES_SOURCE_DIR'])

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .article import article as article_blueprint
    app.register_blueprint(article_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint)

    return app
