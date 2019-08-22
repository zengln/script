# -*- coding:utf-8 -*-


class CustomError(Exception):
    """
    自定义异常类
    """
    def __init__(self, error_msg):
        super().__init__(self)
        self.error_info = error_msg

    def __str__(self):
        return self.error_info
