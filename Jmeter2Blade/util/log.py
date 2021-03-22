# -*- coding:utf-8 -*-
# @Time    : 2021/3/22 15:20
# @Author  : zengln
# @File    : log.py

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(filename)s - %(lineno)d - %(levelname)s - %(message)s')
logger = logging.getLogger("Jmeter2Blade")