# -*- coding:utf-8 -*-
# @Time    : 2021/3/18 14:28
# @Author  : zengln
# @File    : PostBlade.py

import requests
import json
import Jmeter2Blade.util.util as util

from Jmeter2Blade.util.log import logger
from Jmeter2Blade.util.util import random_uuid


class VariableData:
    """
    变量数据处理接口
    """
    def __init__(self, dataNode, data=None, vid="", vName=""):
        self.dataNode = dataNode
        self.api_token = util.TOKEN
        self.account = util.account
        self.vid = vid
        self.vName = vName

        if not data:
            data = []
        self.data = data

    def set_data(self, data):
        if not isinstance(data, dict):
            return False

        self.data.append(data)


class importOfflineCase:
    """
    用例数据导入接口
    """
    def __init__(self, nodePath, data=None, vid="", vName=""):
        self.nodePath = nodePath
        self.api_token = util.TOKEN
        self.account = util.account
        self.vid = vid
        self.vName = vName

        if not data:
            data = []
        self.data = data

    # 添加测试用例
    def add_case(self, casename, step, **kwargs):
        data = dict()
        # 用例类型 1-手工, 2-自动化
        data["caseType"] = "1"
        # 用例状态。0-待设计；1-已启用；2-设计中；3-已废弃
        data["caseState"] = "1"
        # 优先级 P1(高)、P2(中)、P3(低)、P4(极低)
        data["casePrior"] = "P2"
        # 正反用例类型 0-正，1-反
        data["caseSideType"] = "0"
        # 0:功能;1:性能;2:文档;3:安全;4:兼容性;5:可靠性;6:用户体验;7:安装部署;
        data["caseDetailType"] = "0"
        # 负责人
        data["caseHeader"] = util.account
        # 审核状态 0.待审核,1审核通过,2审核不通过,3免审核4未提交审核
        data["caseReviewStatus"] = "3"
        # 标签
        data["caseKeyword"] = "Jmeter转Blade用例"
        data["caseName"] = casename
        data["step"] = step

        if kwargs:
            for key, value in kwargs.items():
                data[key] = value

        self.data.append(data)


class importOfflineCase_step:

    def __init__(self, step_name="", step_des=""):
        self.step = dict()
        self.step_json = dict()
        # 初始化 step
        self.step["stepName"] = step_name
        self.step["stepJson"] = self.step_json
        # 初始化 step_json
        self.step_json["stepDes"] = step_des
        self.step_json["Expect"] = ""
        self.step_json["inputData"] = ""
        self.step_json["precisionTest"] = "2"
        self.step_json["preSqlContent"] = list()
        self.step_json["scriptContent"] = ""
        self.step_json["dataContent"] = dict()
        self.step_json["checkContent"] = list()
        self.step_json["stepExcute"] = ""

    def get_step(self):
        return self.step

    def set_stepname(self, step_name):
        self.step["stepName"] = step_name

    def set_stepdes(self, step_des):
        self.step_json["stepDes"] = step_des

    def set_expect(self, expect):
        self.step_json["Expect"] = expect

    def set_inputdata(self, input_data):
        self.step_json["inputData"] = input_data

    def set_presqlcontent(self, presqlcontent):
        self.step_json["preSqlContent"] = presqlcontent

    def add_presqlcontent(self, data_source, sql):
        pre_sql = {
            "connection": data_source,
            "id": "",
            "type": "2",
            "content": "%s" % sql
        }
        self.step_json["preSqlContent"].append(pre_sql)

    def set_scriptcontent(self,scriptcontent):
        self.step_json["scriptContent"] = scriptcontent

    def set_datacontent(self, datacontent):
        self.step_json["dataContent"] = datacontent

    def set_checkcontent(self, checkcontent):
        self.step_json["checkContent"] = checkcontent

    def add_checkcontent(self, checkcontent):
        self.step_json["checkContent"].append(checkcontent)

    def set_stepexcute(self, stepexcute):
        self.step_json["stepExcute"] = stepexcute

    def set_dataarrcontent(self, dataarrcontent):
        data_content = self.step_json["dataContent"]
        data_content["id"] = ""
        data_content["dataChoseRow"] = ""
        data_content["content"] = ""
        data_content["dataArrContent"] = dataarrcontent

    def set_default_dataarrcontent(self):
        default_data_content = list()
        temp = dict()
        temp["sheet0"] = list()
        one = [random_uuid(32), "序号", "期望"]
        two = [random_uuid(32), "参数说明", ""]
        temp["sheet0"].append(one)
        temp["sheet0"].append(two)
        default_data_content.append(temp)

        data_content = self.step_json["dataContent"]
        data_content["id"] = ""
        data_content["dataChoseRow"] = ""
        data_content["content"] = ""
        data_content["dataArrContent"] = default_data_content


class dealScriptData:
    """
    脚本处理接口, 可以自行传入数据, 或者使用默认模版(后续可能调整)
    """
    def __init__(self, data_node, data=None, vid="", vName=""):
        self.dataNode = data_node
        self.vid = vid
        self.vName = vName
        self.account = util.account
        self.api_token = util.TOKEN

        if not data:
            data = []
        self.data = data

    def set_data(self, data):
        if not isinstance(data, dict):
            return False

        self.data.append(data)

    def set_data_with_default(self, script_name, root_url, path, script_remark=""):
        data = {
          "scriptName": "%s" % script_name,
          "scriptContent": "http|%s,%s,POST,UTF-8,json,Content-Type=application/json;charset=UTF-8,,300" % (root_url, path),
          "scriptRemark": "%s" % script_remark,
          "scriptJsonData": {"根URL": "%s" % root_url, "路径": "%s" % path, "请求方式": "POST", "编码类型": "UTF-8", "返回形式": "json",
                             "header配置": "Content-Type=application/json;charset=UTF-8", "精准标签": "",
                             "超时时间": "300"}
        }
        logger.info(data)
        self.data.append(data)


class PostBlade:
    """
    与Blade通信, 将发送与接收返回信息后的数据提取公共化
    """
    SUCCESS = 'success'

    proxies = {
        "http": 'http://127.0.0.1:8080',
        "https": 'http://127.0.0.1:8080'
    }

    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
        }

    # blade接口-添加自定义变量
    def dealVariableData(self, data):
        if not isinstance(data, VariableData):
            return "data 需要为VariableData实例"
        resp = requests.post(util.dealVariableData_url, data=json.dumps(data.__dict__), headers=self.headers)
        content = resp.content.decode("utf-8")
        resp_content_json = json.loads(content)
        logger.info(resp_content_json)
        if resp_content_json['msg'] == PostBlade.SUCCESS and resp_content_json['sub_msg'] == "":
            return
        else:
            return resp_content_json['sub_msg']

    # blade 接口-添加测试用例
    def importOfflineCase(self, data):
        if not isinstance(data, importOfflineCase):
            return "data需要为importOfflineCase实例"
        resp = requests.post(util.importOfflineCase_url, data=json.dumps(data.__dict__), headers=self.headers)
        content = resp.content.decode("utf-8")
        resp_content_json = json.loads(content)
        logger.info(resp_content_json)
        if resp_content_json['msg'] == PostBlade.SUCCESS and resp_content_json['sub_msg'] == "":
            return
        else:
            return resp_content_json['sub_msg']

    # blade 接口-脚本数据处理接口
    def dealScriptData(self, data):
        if not isinstance(data, dealScriptData):
            return "data 需要为 dealScriptData 实例"
        resp = requests.post(util.dealScriptData_url, data=json.dumps(data.__dict__), headers=self.headers)
        content = resp.content.decode("utf-8")
        resp_content_json = json.loads(content)
        logger.info(resp_content_json)
        if resp_content_json['msg'] == PostBlade.SUCCESS and resp_content_json['sub_msg'] == "":
            return None, resp_content_json['result_list'][0]['ID']
        else:
            return resp_content_json['sub_msg'], resp_content_json['result_list'][0]['ID']


if __name__ == "__main__":
    # vd = VariableData("自定义变量", [{"varName": "varc_test", "varContent": 3, "variableRemark":"python"}])
    # pb = PostBlade()
    # pb.dealVariableData(vd)
    ds = dealScriptData(data_node="jmeter转blade测试/")
    ds.set_data_with_default(script_name="FROMPYTHON", root_url="iibs_config", path="/python", script_remark="Python备注")
    pb = PostBlade()
    logger.info(pb.dealScriptData(ds))








