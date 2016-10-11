import os

from flask import current_app


class Article(object):

    sc_dir = current_app.config['ARTICLES_SOURCE_DIR']
    ds_dir = current_app.config['ARTICLES_DESTINATION_DIR']

    """ 根据文件名构造相关信息 """
    def __init__(self, filename):
        if filename.endswith(('.md', '.html')):
            self.name = filename.split('.')[0]
        else:
            self.name = filename
        self.md_name = self.name + '.md'
        self.html_name = self.name + '.html'
        self.sc_path = os.path.join(self.sc_dir, self.md_name)
        self.ds_path = os.path.join(self.ds_dir, self.html_name)
