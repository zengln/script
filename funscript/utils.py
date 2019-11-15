# -*- coding:utf-8 -*-
# @Time    : 2019/11/14 8:56
# @Author  : zengln
# @File    : utils.py

import json


def diff_response(resp_obj, excepted_resp_json):
    diff_content = {}
    resp_info = parse_response_object(resp_obj)

    diff_content = diff_json(resp_info, excepted_resp_json)

    return diff_content


def parse_response_object(resp_obj):
    try:
        resp_body = resp_obj.json()
    except ValueError:
        resp_body = resp_obj.text

    return {
        'status_code': resp_obj.status_code,
        'headers': resp_obj.headers,
        'body': resp_body
    }


def diff_json(current_json, excepted_json):
    json_diff = {}

    for key, excepted_value in excepted_json.items():
        value = current_json.get(key, None)
        if str(value) != str(excepted_value):
            json_diff[key] = {
                'value': value,
                'excepted': excepted_value
            }

    return json_diff


def load_testcases(testcase_file_path):
    with open(testcase_file_path, "r") as testcase_file:
        json_data = json.load(testcase_file)

    return json_data
