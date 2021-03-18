# -*- coding:utf-8 -*-
# @Time    : 2021/3/18 14:28
# @Author  : zengln
# @File    : PostBlade.py

import requests
import json
import Jmeter2Blade.util.util as util


class VariableData:

    def __init__(self, dataNode, data, vid="", vName=""):
        self.dataNode = dataNode
        self.data = data
        self.api_token = util.TOKEN
        self.account = util.account
        self.vid = vid
        self.vName = vName


class importOfflineCase:

    def __init__(self, nodePath, data, vid="", vName=""):
        self.nodePath = nodePath
        self.data = data
        self.api_token = util.TOKEN
        self.account = util.account
        self.vid = vid
        self.vName = vName


class PostBlade:
    SUCCESS = 'success'

    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
        }

    # blade接口-添加自定义变量
    def dealVariableData(self, data):
        if not isinstance(data, VariableData):
            return
        resp = requests.post(util.dealVariableData_url, data=json.dumps(data.__dict__), headers=self.headers)
        content = resp.content.decode("utf-8")
        resp_content_json = json.loads(content)
        print(resp_content_json)
        if resp_content_json['msg'] == PostBlade.SUCCESS and resp_content_json['sub_msg'] == "":
            return
        else:
            return resp_content_json['sub_msg']


    # blade 接口-添加测试用例
    def importOfflineCase(self, data):
        if not isinstance(data, importOfflineCase):
            return
        resp = requests.post(util.importOfflineCase_url, data=json.dumps(data.__dict__), headers=self.headers)
        content = resp.content.decode("utf-8")
        resp_content_json = json.loads(content)
        print(resp_content_json)
        if resp_content_json['msg'] == PostBlade.SUCCESS and resp_content_json['sub_msg'] == "":
            return
        else:
            return resp_content_json['sub_msg']



if __name__ == "__main__":
    vd = VariableData("/自定义变量", [{"varName": "varc_test", "varContent": 3, "variableRemark":"python"}])
    pb = PostBlade()
    pb.dealVariableData(vd)







