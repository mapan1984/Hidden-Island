import os

from flask import current_app


class Article(object):
    """ 根据文件名xxx[.md]构造相关信息 """
    def __init__(self, filename):
        if filename.endswith('.md'):
            self.name = filename.split('.')[0]
            self.md_name = filename
        else:
            self.name = filename
            self.md_name = filename + '.md'
        self.html_name = self.name + '.html'
        self.sc_path = os.path.join(
            current_app.config['ARTICLES_SOURCE_DIR'], self.md_name)
        self.ds_path = os.path.join(
            current_app.config['ARTICLES_DESTINATION_DIR'], self.html_name)
