import os
import logging

import redis
from celery import Celery
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown

from config import config


FLASK_ENV = os.getenv('FLASK_ENV') or 'default'

bootstrap = Bootstrap()
moment = Moment()
pagedown = PageDown()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
pagedown = PageDown()

celery = Celery(
    __name__,
    backend=config[FLASK_ENV].CELERY_RESULT_BACKEND,
    broker=config[FLASK_ENV].CELERY_BROKER_URL,
)

redis = redis.from_url(config[FLASK_ENV].REDIS_URL, decode_responses=True)



def update_celery(celery, app):

    backend = app.config['CELERY_RESULT_BACKEND']
    if backend:
        celery._Celery__autoset('result_backend', backend)

    broker = app.config['CELERY_BROKER_URL']
    if broker:
        celery._Celery__autoset('broker_url', broker)

    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    pagedown.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    # HACK: update celery
    global celery
    update_celery(celery, app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .article import article as article_blueprint
    app.register_blueprint(article_blueprint, url_prefix='/article')

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/user')

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app


# HACK: get the flask app logger
logger = logging.getLogger('flask.app')
