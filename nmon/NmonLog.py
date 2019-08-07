# -*- coding:utf-8 -*-

# create: 2019-07-29
# author:zengln
# desc: 日志输出

import logging


class nmonlog(object):
    log = None

    @classmethod
    def init_log(cls):
        if cls.log is None:
            logger = logging.Logger("nmon_analyse")
            handler_std = logging.StreamHandler()
            handler_log = logging.FileHandler(filename="error.log", encoding="utf-8")

            logger.setLevel(logging.DEBUG)
            handler_std.setLevel(logging.INFO)
            handler_log.setLevel(logging.ERROR)

            formatter = logging.Formatter("%(asctime)s %(name)s:%(levelname)s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
            handler_std.setFormatter(formatter)
            handler_log.setFormatter(formatter)

            logger.addHandler(handler_std)
            logger.addHandler(handler_log)
            cls.log = logger

        return cls.log


