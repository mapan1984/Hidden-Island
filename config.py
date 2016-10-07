import os

base_dir = os.path.abspath(os.path.dirname(__file__))

class config:
    DEBUG = True
    SECRET_KEY = "hard to guess string"
    ARTICLES_SOURCE_DIR = os.path.join(base_dir, 'articles')
    ARTICLES_DESTINATION_DIR = os.path.join(base_dir, 'app','templates','articles')


    @staticmethod
    def init_app(app):
        pass
