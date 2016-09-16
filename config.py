import os

base_dir = os.path.abspath(os.path.dirname(__file__))

class config:
    DEBUG = True
    ARTICLES_DIR = os.path.join(base_dir, 'articles')

    @staticmethod
    def init_app(app):
        pass