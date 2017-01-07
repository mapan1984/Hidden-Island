import os

base_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = True
    # 表单
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hard_to_guess_string')
    # 数据库
    SQLALCHEMY_DATABASE_URI = \
            'sqlite:///' + os.path.join(base_dir, 'data.sqlite')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 文章目录
    ARTICLES_SOURCE_DIR = os.path.join(base_dir, 'articles')
    ARTICLES_DESTINATION_DIR = os.path.join(base_dir, 'app',
                                            'templates', 'articles')

    # 上传文件 
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    @staticmethod
    def init_app(app):
        pass
