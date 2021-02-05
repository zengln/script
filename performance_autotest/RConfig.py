# -*- coding:utf-8 -*-

import configparser
import os

from performance_autotest.customexception import CustomError


class Config(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        else:
            raise CustomError("Config 类只能含有一个实例, "
                              "使用类方法 get_instance 获取实例")

        return cls.__instance

    def reload_all_value(self, config_file):
        self.conf = configparser.ConfigParser()

        # 「优化」自行传入配置文件,
        if not config_file:
            # 没传入读取默认配置
            config_path = os.path.dirname(__file__)
            config_file = config_path + "\\conf\\config.ini"

        if os.path.exists(config_file):
            self.conf.read(config_file)
        else:
            raise CustomError("配置文件不存在")

        sections = self.conf.sections()
        for section in sections:
            items = self.conf.items(section)
            for item in items:
                if not self.set_default_value(item):
                    self.__setattr__(item[0], item[1].strip())
                # 替换路径
                if item[0] in ['download_local_path', 'jmeter_script_dir', 'report_path']:
                    self.replace_path(item[1])

    @classmethod
    def get_instance(cls, config_file=""):
        if not cls.__instance:
            cls.__instance = Config()

        cls.__instance.reload_all_value(config_file)
        return cls.__instance

    def set_default_value(self, section_item):
        if section_item[1]:
            return

        if section_item[0] == "nmon_path":
            self.__setattr__(section_item[0], ".")
        elif section_item[0] == "nmon_acquisition_interval":
            self.__setattr__(section_item[0], "1")
        elif section_item[0] == "download_local_path":
            raise CustomError("存放监控文件路径不能为空")
        elif section_item[0] == "remote_host_num":
            raise CustomError("后台服务器数量不能为空")
        elif section_item[0] == "report_name":
            self.__setattr__(section_item[0], "report.html")
        elif section_item[0] == "run_in_win":
            self.__setattr__(section_item[0], "1")
        else:
            self.__setattr__(section_item[0], "")

        return True

    def replace_path(self, replace_path):
        """
        替换 widnows 上路径分隔符
        例如 C:/test/index.txt
        替换成 c:\test\index.txt
        :param value:
        :return:
        """
        if "/" in replace_path:
            replace_path.replace('/', '\\')
        return replace_path