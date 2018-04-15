import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hard_to_guess_string')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

# Mail_Config {{
    MAIL_SUBJECT_PREFIX = '[HIDDEN-ISLAND]'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
    MAIL_SENDER = os.environ.get('MAIL_SENDER')
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
# end_mail_config }}

    # 文章目录
    ARTICLES_SOURCE_DIR = os.path.join(BASE_DIR, 'articles')
    # 每页文章数
    ARTICLES_PAGINATE = 7
    # 每页评论数
    COMMENTS_PAGINATE = 7
    # 上传文件大小限制
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    # 允许上传的文件后缀
    ALLOWED_EXTENSIONS = set(['md', 'markdown'])

    @classmethod
    def allowed_file(cls, filename):
        return '.' in filename \
               and filename.rsplit('.', 1)[1] in cls.ALLOWED_EXTENSIONS

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'data.sqlite')

    @classmethod
    def init_app(cls, app_):
        Config.init_app(app_)

        # email errors to the administrators
        import logging
        from app.utils.log_handler import SendGridMailHandler
        mail_handler = SendGridMailHandler(
            api_key=os.getenv("SENDGRID_API_KEY"),
            sender=cls.MAIL_SENDER,
            recipient=cls.ADMIN_EMAIL,
            subject=cls.MAIL_SUBJECT_PREFIX + 'Application error!'
        )
        mail_handler.setFormatter(logging.Formatter('''
            Message type:       %(levelname)s
            Location:           %(pathname)s:%(lineno)d
            Module:             %(module)s
            Function:           %(funcName)s
            Time:               %(asctime)s

            Message:

            %(message)s
        '''))
        mail_handler.setLevel(logging.ERROR)
        app_.logger.addHandler(mail_handler)


class HerokuConfig(ProductionConfig):

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,

    'default': DevelopmentConfig
}
