# -*- coding:utf-8 -*-
# @Time    : 2019/11/14 8:40
# @Author  : zengln
# @File    : test_runner.py

import requests
from . import exception, utils

"""
测试用例执行引擎
"""


def run_single_testcase(testcase):
    req_kwargs = testcase['request']

    try:
        url = req_kwargs.pop('url')
        method = req_kwargs.pop('method')
    except KeyError:
        raise exception.ParamsError("Params Error")

    resp_obj = requests.request(url=url, method=method, **req_kwargs)
    diff_content = utils.diff_response(resp_obj, testcase['response'])
    success = False if diff_content else True

    return success, diff_content
