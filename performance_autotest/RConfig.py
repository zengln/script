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

    def __init__(self):
        self.conf = configparser.ConfigParser()
        config_path = os.path.dirname(__file__)
        if os.path.exists(config_path+"\\conf\\config.ini"):
            self.conf.read(config_path+"\\conf\\config.ini", encoding="GBK")
        else:
            raise CustomError("配置文件不存在")

    def reload_all_value(self):
        sections = self.conf.sections()
        for section in sections:
            items = self.conf.items(section)
            for item in items:
                if not self.set_default_value(item):
                    self.__setattr__(item[0], item[1])

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = Config()
            cls.__instance.reload_all_value()
        return cls.__instance

    def set_default_value(self, section_item):
        if not section_item[1] == "":
            return False

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
        else:
            self.__setattr__(section_item[0], "")

        return True