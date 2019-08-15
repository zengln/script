# -*- coding:utf-8 -*-


class NmonException(Exception):

    def __init__(self, error_msg):
        self.value = error_msg

    def __str__(self):
        return self.value