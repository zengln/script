# -*- coding:utf-8 -*-
# @Time    : 2019/8/29 10:49
# @Author  : zengln
# @File    : Log.py

import logging
import traceback
import sys
import time

from performance_autotest.customexception import CustomError
from performance_autotest.RConfig import Config


class Log(object):
    """
    全局Log,单例
    """
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        else:
            raise CustomError("Log 只能存在一个实例")

        return cls.__instance

    def __init__(self, debug_flag=False):
        log = logging.Logger("performance_autotest")

        handler_console = logging.StreamHandler()
        handler_logfile = logging.FileHandler(filename="error.log", encoding='utf-8')

        log.setLevel(logging.DEBUG)
        handler_logfile.setLevel(logging.ERROR)
        if debug_flag:
            handler_console.setLevel(logging.DEBUG)
        else:
            handler_console.setLevel(logging.INFO)

        fmt = logging.Formatter("[%(asctime)s %(levelname)5s %(filename)s-%(funcName)s]: %(message)s ",
                                datefmt="%Y-%m-%d %H:%M:%S")

        handler_console.setFormatter(fmt)
        handler_logfile.setFormatter(fmt)

        log.addHandler(handler_logfile)
        log.addHandler(handler_console)

        self.log = log

    def get_log(self):
        return self.log


try:
    config = Config.get_instance()
    if hasattr(config, "debug_mode") and str.upper(config.debug_mode) == "TRUE":
        logger = Log(True).get_log()
    else:
        logger = Log().get_log()
except Exception:
    error_msg = traceback.format_exc()
    print(error_msg)
    time.sleep(1)
    input("按任意键退出")
    sys.exit()
