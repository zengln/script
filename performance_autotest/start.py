# -*- coding:utf-8 -*-
# @Time    : 2019/8/27 9:58
# @Author  : zengln
# @File    : start.py

from performance_autotest import launch
from performance_autotest.log import logger
import time
import sys
import traceback

"""
    入口脚本
"""

try:
    script_launch = launch.Launch()
    script_launch.start()
except Exception:
    error_msg = traceback.format_exc()
    logger.error(error_msg)
finally:
    time.sleep(1)
    input("按任意键退出")
    sys.exit()
