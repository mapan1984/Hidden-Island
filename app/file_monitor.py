import os
import json
import hashlib

class FileMonitor(object):
    """ 构造一个目录file_dir的监测器 """
    def __init__(self, file_dir):
        # 需监测的文件的目录
        self.file_dir = file_dir
        # 文件的绝对路径列表(读取文件时使用)
        self.ab_path_list = [os.path.join(self.file_dir, filename) \
                              for filename in os.listdir(self.file_dir)]
        # 文件名列表(保存log时使用)
        self.filename_list = [os.path.split(path)[-1] \
                               for path in self.ab_path_list]
        self.log_file = os.path.join(os.getcwd(), "file_log.json")
        try:
            with open(self.log_file, "r") as log:
                self.log_kv = json.load(log)
        except json.JSONDecodeError as e:
            print(e)
            self._init_log()

    @staticmethod
    def get_file_md5(filename):
        """ 由文件名(绝对路径)返回文件md5值 """
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

    def _refresh_log(self):
        """ 保存当前kv """
        with open(self.log_file, "w", encoding='utf-8') as log_file:
            json.dump(self.log_kv, log_file, sort_keys=True, indent=4)

    def is_change(self, filename):
        old_file_hash = self.log_kv.get(filename)
        file_hash = FileMonitor.get_file_md5(os.path.join(self.file_dir, filename))
        if old_file_hash is None or file_hash != self.log_kv[filename]:
            self.log_kv[filename] = file_hash
            self._refresh_log()
            return True
        else:
            return False

    def _init_log(self):
        """ 初始化log """
        # {"xxx.md":"md5 of xxx.md"}
        self.log_kv = {os.path.split(ab_path)[-1]:FileMonitor.get_file_md5(ab_path) \
                                for ab_path in self.ab_path_list}
        self._refresh_log()
