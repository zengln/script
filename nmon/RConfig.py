# -*- coding:utf-8 -*-

import configparser
import os
import sys

from nmon.NmonLog import log


class Config(object):

    def __init__(self):
        self.conf = configparser.ConfigParser()
        if os.path.exists(".\\config\\config.ini"):
            self.conf.read(".\\config\\config.ini", encoding="utf-8-sig")
        else:
            log.error("请确认配置文件 config.ini 是否存在")
            sys.exit()

    def reload_all_value(self):
        sections = self.conf.sections()
        for section in sections:
            items = self.conf.items(section)
            for item in items:
                self.__setattr__(item[0], item[1])

