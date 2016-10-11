import os
import json
import hashlib

from app.generate import generate

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

class FileMonitor(object):
    """ 构造一个目录file_dir的监测器 """
    def __init__(self, file_dir):
        # 需监测的文件的目录
        self.file_dir = file_dir
        # 文件的绝对路径列表(读取文件时使用)
        self.ab_path_list = [os.path.join(self.file_dir, filename) \
                             for filename in os.listdir(self.file_dir)]
        # md文件名列表(保存log时使用)
        self.filename_list = [os.path.split(path)[-1] \
                              for path in self.ab_path_list]
        # 记录json文件path
        self.log_file = os.path.join(os.getcwd(), "file_log.json")
        # self.log_kv = {filename:file_md5}
        try:
            # log_file存在记录值 
            with open(self.log_file, "r") as log:
                self.log_kv = json.load(log)
        except (FileNotFoundError,json.JSONDecodeError) as e:
            print(e)
            self._init_log()
        finally:
            print("monitor init")

    def _init_log(self):
        # 初始化log_kv和记录log_file
        # {"xxx.md":"md5 of xxx.md"}
        self.log_kv = {os.path.split(ab_path)[-1]:get_file_md5(ab_path) \
                       for ab_path in self.ab_path_list}
        self.refresh_log()


    def is_change(self, filename):
        """ 判断md文件是否(不存在或改变), 是则更新log_kv
        argv:
            filename: md文件名(xxx.md)
        """
        old_file_md5 = self.log_kv.get(filename)
        now_file_md5 = get_file_md5(os.path.join(self.file_dir, filename))
        if old_file_md5 != now_file_md5:
            self.log_kv[filename] = now_file_md5
            return True
        else:
            return False

    def refresh_path(self):
        print("refresh_path")
        # 文件的绝对路径列表(读取文件时使用)
        self.ab_path_list = [os.path.join(self.file_dir, filename) \
                             for filename in os.listdir(self.file_dir)]
        # md文件名列表(保存log时使用)
        self.filename_list = [os.path.split(path)[-1] \
                              for path in self.ab_path_list]

    def refresh_kv(self):
        """ 如果无文件存在而有log_kv，删除相应log_kv """
        print("refresh_kv")
        has_log_md = {filename for filename in self.log_kv.keys()}
        existed_md = {filename for filename in self.filename_list}
        for filename in has_log_md - existed_md:
            del self.log_kv[filename]
        for filename in existed_md - has_log_md:
            self.log_kv[filename] = \
                    get_file_md5(os.path.join(self.file_dir, filename))

    def refresh_log(self):
        """ 更新md文件log记录 """
        print("refresh_log")
        with open(self.log_file, "w", encoding='utf-8') as log_file:
            json.dump(self.log_kv, log_file, sort_keys=True, indent=4)
