import os
import json
import hashlib

from app.article_info import Article


def get_file_md5(filename):
    """ 由文件绝对路径返回文件md5值 """
    if not os.path.isfile(filename):
        print("%s is not a file" % filename)
    hs = hashlib.md5()
    fd = open(filename, "rb")
    while True:
        content = fd.read(1024)
        if not content:
            break
        hs.update(content)
    fd.close()
    return hs.hexdigest()

class ArticleLog(object):
    """ 构造一个目录article_dir的记录 """
    def __init__(self, article_dir):
        self.article_dir = article_dir
        self.log_file = os.path.join(os.getcwd(), "file_log.json")
        self.article_list = \
                [Article(md_name) for md_name in os.listdir(self.article_dir)]
        try:
            with open(self.log_file, "r") as log:
                self.log_kv = json.load(log)
        except (FileNotFoundError,json.JSONDecodeError) as e:
            print(e)
            self.log_kv = {file.name:get_file_md5(file.sc_path) \
                           for file in self.article_list}
            self.refresh_log()

    def is_change(self, file):
        """ 判断md文件是否(不存在或改变), 是则更新log_kv """
        old_file_md5 = self.log_kv.get(file.name)
        now_file_md5 = get_file_md5(file.sc_path)
        if old_file_md5 != now_file_md5:
            self.log_kv[file.name] = now_file_md5
            return True
        else:
            return False

    def _refresh_article_list(self):
        self.article_list = \
                [Article(md_name) for md_name in os.listdir(self.article_dir)]

    def _refresh_kv(self):
        """
        如果无文件存在而有log_kv，删除相应log_kv
        如果有文件而无相应log_kv，则添加kog_kv
        """
        has_log = {filename for filename in self.log_kv.keys()}
        existed = {file.name for file in self.article_list}
        for filename in has_log - existed:
            del self.log_kv[filename]
        for filename in existed - has_log:
            self.log_kv[filename] = get_file_md5(Article(filename).sc_path)

    def _refresh_log(self):
        """ 更新md文件log记录 """
        with open(self.log_file, "w", encoding='utf-8') as log_file:
            json.dump(self.log_kv, log_file, sort_keys=True, indent=4)

    def refresh(self):
        self._refresh_article_list()
        self._refresh_kv()
        self._refresh_log()
