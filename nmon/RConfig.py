# -*- coding:utf-8 -*-

import configparser


class Config(object):

    def __init__(self):
        self.conf = configparser.ConfigParser()
        self.conf.read(".\\config\\config.ini", encoding="utf-8-sig")

    def reload_all_value(self):
        sections = self.conf.sections()
        for section in sections:
            items = self.conf.items(section)
            for item in items:
                self.__setattr__(item[0], item[1])

