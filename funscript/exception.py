# -*- coding:utf-8 -*-
# @Time    : 2019/11/14 8:47
# @Author  : zengln
# @File    : exception.py


class ParamsError(BaseException):

    def __init__(self, error_msg):
        super().__init__(self)
        self.error_info = error_msg

    def __str__(self):
        return self.error_info
