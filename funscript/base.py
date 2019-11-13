# -*- coding:utf-8 -*-
# @Time    : 2019/11/13 9:04
# @Author  : zengln
# @File    : base.py

import multiprocessing
import unittest
import time

from .api_server import app as flask_app


def run_flask():
    flask_app.run()


class ApiServerUnittest(unittest.TestCase):

    """
    启动用来测试的HTTP服务
    """

    @classmethod
    def setUpClass(cls):
        cls.api_server_process = multiprocessing.Process(
            target=run_flask
        )
        cls.api_server_process.start()
        time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.api_server_process.terminate()



