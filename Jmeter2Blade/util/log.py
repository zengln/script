# -*- coding:utf-8 -*-
# @Time    : 2021/3/22 15:20
# @Author  : zengln
# @File    : log.py

from colorlog import ColoredFormatter
import logging

LOG_LEVEL = logging.INFO


log_format = "%(log_color)s%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s%(reset)s"

colored_formatter = ColoredFormatter(log_format)
logger = logging.getLogger("Jmeter2Blade")
stream = logging.StreamHandler()
stream.setLevel(LOG_LEVEL)
stream.setFormatter(colored_formatter)

logger.addHandler(stream)
logger.setLevel(LOG_LEVEL)