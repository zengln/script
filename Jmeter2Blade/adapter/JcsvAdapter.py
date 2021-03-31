# -*- coding:utf-8 -*-
# @Time    : 2021/3/18 10:55
# @Author  : zengln
# @File    : JcsvAdapter.py

import os
import xml.etree.ElementTree as ET
import json
import re

from Jmeter2Blade.socket.PostBlade import VariableData, PostBlade, dealScriptData, importOfflineCase
from Jmeter2Blade.util.log import logger
from Jmeter2Blade.util.JmeterElement import JmeterElement
from Jmeter2Blade.util.util import random_uuid


def Josn2Blade(message,  result, num=0, check_Message=""):
    """
    将报文转化为Blade可接收的测试数据格式
    :param message: 报文数据
    :param num: sheet计数
    :param result: Blade 数据格式
    :param check_Message: 验证字符串
    :return:
    """
    temp = dict()
    temp["sheet"+str(num)] = []
    result.append(temp)
    dict_num = 0
    # 0 特殊处理
    if num == 0:
        one = [random_uuid(32), "序号", "期望"]
        two = [random_uuid(32), "参数说明", ""]
        three = [random_uuid(32), "", check_Message]
        temp["sheet"+str(num)].append(one)
        temp["sheet"+str(num)].append(two)
        temp["sheet"+str(num)].append(three)
    else:
        one = [random_uuid(32), "GroupID"]
        two = [random_uuid(32), "1"]
        temp["sheet"+str(num)].append(one)
        temp["sheet"+str(num)].append(two)

    for key, value in message.items():
        if isinstance(value, dict):
            dict_num += 1
            temp["sheet" + str(num)][0].append(key+"(object)")
            temp["sheet" + str(num)][-1].append("sheet"+str(num+dict_num)+"|1")
            Josn2Blade(value, result, num+dict_num)
        else:
            temp["sheet"+str(num)][0].append(key)
            temp["sheet"+str(num)][-1].append(value)

    return result


# CSV 文件处理
def deal_csv_file(filename):
    # 给的脚本里文件绝对路径与本机不同
    # 所有只需要脚本名称, 直接从项目的路径下取文件
    csv_file = open(r"../file/"+filename, encoding="utf8")
    # 数据长度不一定, 通过 yq_respCode 字段定位报文结束位置
    message_stop_index = 0
    titles = csv_file.readline().split(",")
    for title in titles:
        if title == "yq_respCode":
            message_stop_index = titles.index(title)
            break

    messages = []
    for line in csv_file.readlines():
        temp = dict()
        message = dict()
        data = line.split(",")[0:message_stop_index]
        logger.info(data)
        for i in range(1, len(data)):
            temp[titles[i]] = data[i]

        message["casename"] = data[0]
        message["body"] = json.dumps(temp)
        messages.append(message)

    return messages


# 自定义变量组件处理
def deal_arguments(root, node_name, arguments_local=None):
    variable_date = VariableData(node_name)
    for child in root.element[0]:
        data = dict()

        var_name = child.find(".//stringProp[@name='Argument.name']")
        if var_name is not None:
            data["varName"] = var_name.text

        var_content = child.find(".//stringProp[@name='Argument.value']")
        if var_content is not None:
            data["varContent"] = var_content.text

        variable_remark = child.find(".//stringProp[@name='Argument.desc']")
        if variable_remark is not None:
            data["variableRemark"] = variable_remark.text

        # 本地化处理
        arguments_local[var_name.text] = var_content.text
        variable_date.set_data(data)

    resp = post_blade.dealVariableData(variable_date)
    # logger.info(resp)
    if resp is not None:
        logger.error(resp)


# HTTP 请求组件处理
def deal_HTTPSampler(root, step_name, script_content, request_body=""):
    # 响应验证字段
    match_string = ""
    # 报文提取
    step = dict()
    step_json = dict()
    data_content = dict()
    step["stepName"] = step_name
    step["stepJson"] = step_json
    step_json["dataContent"] = data_content
    step_json["stepDes"] = root.get("testname")
    # 0—前置，1-后置，2-空
    step_json["precisionTest"] = "1"
    pre_sqls = list()
    step_json["preSqlContent"] = pre_sqls
    step_json["scriptContent"] = script_content
    # 没有传入报文内容, 自行获取当前报文内容, 否则使用传入内容
    if not request_body:
        request_body = root.element.find(".//stringProp[@name='Argument.value']").text

    sub_elements = root.get_sub_elements()
    for sub_element in sub_elements:
        # 前置提取
        if sub_element.tag == "JDBCPreProcessor":
            sql = sub_element.element.find(".//stringProp[@name='query']").text
            logger.info(sql)
            pre_sql = {
                    "id": "",
                    "type": "2",
                    "content": "%s" % sql
                    }
            pre_sqls.append(pre_sql)
        # 后置提取
        # 验证提取
        elif sub_element.tag in ("ResponseAssertion", "BeanShellAssertion"):
            match_string = sub_element.element.find(".//collectionProp[@name='Asserion.test_strings']")[0].text

    data_content["dataArrContent"] = Josn2Blade(eval(request_body), [], 0, match_string)
    data_content["id"] = ""
    data_content["dataChoseRow"] = ""
    data_content["content"] = ""

    logger.debug(step)
    return step


# 线程组组件
def deal_threadgroup(root, node_path):
    # csv 标识
    csv_flag = False
    # 线程组名称, 作为用例节点的父级目录名称
    thread_group_name = root.get("testname")
    logger.info(node_path)
    sub_elements = root.get_sub_elements()

    # 如果是csv格式的,包含了控制器,特殊处理
    if sub_elements[0].tag == "TransactionController":
        sub_elements = sub_elements[0].get_sub_elements()
        csv_flag = True

    messages = []
    for sub_element in sub_elements:
        if csv_flag:
            # csv 处理, 获取所有报文
            # 从 Beanshell 中将读取的csv文件key取出
            if sub_element.tag == "BeanShellSampler":
                java_code = sub_element.element.find(".//stringProp[@name='BeanShellSampler.query']").text
                # 获取csv 路径 key
                csv_re = re.compile(r'FileInputStream[(]vars.get[(]"(.*?)"[)]', re.S)
                csv_key = re.findall(csv_re, java_code)[0]
                file_path = arguments_local[csv_key]
                logger.info(file_path)
                filename = file_path.split("/")[-1]
                logger.info(filename)
                messages = deal_csv_file(filename)
                logger.debug(messages)
            elif sub_element.tag == "HTTPSamplerProxy":
                path = sub_element.element.find(".//stringProp[@name='HTTPSampler.path']").text
                # 先添加脚本
                ds = dealScriptData(node_path)
                ds.set_data_with_default(thread_group_name, "iibs_config", path, thread_group_name)
                resp, script_id = post_blade.dealScriptData(ds)
                if resp is not None:
                    logger.error(resp)
                # 再添加数据
                request_body_half = sub_element.element.find(".//stringProp[@name='Argument.value']").text
                ioc = importOfflineCase(node_path + thread_group_name)
                for message in messages:
                    requst_body = request_body_half.replace("${req_body}", message["body"])
                    step = deal_HTTPSampler(sub_element, "步骤-1", script_id, requst_body)
                    ioc.add_case(message["casename"], [step])

                resp = post_blade.importOfflineCase(ioc)
                # logger.info(resp)
                if resp is not None:
                    logger.error(resp)

        elif sub_element.tag == "HTTPSamplerProxy":
            path = sub_element.element.find(".//stringProp[@name='HTTPSampler.path']").text
            # 先添加脚本
            ds = dealScriptData(node_path)
            ds.set_data_with_default(thread_group_name, "iibs_config", path, thread_group_name)
            _, script_id = post_blade.dealScriptData(ds)
            # 再添加用例数据
            step = deal_HTTPSampler(sub_element, "步骤-1", script_id)
            ioc = importOfflineCase(node_path + thread_group_name)
            ioc.add_case(thread_group_name, [step])
            resp = post_blade.importOfflineCase(ioc)
            # logger.info(resp)
            if resp is not None:
                logger.error(resp)


# 定义blade根路径
balde_root_name = "jmeter转blade测试"
# 读取xml文件
tree = ET.parse('movie.jmx')
# 获取xml根节点
root = tree.getroot()
# 找到TestPlan组件, 获取blade二级路径名
test_plan = root[0][0]
logger.info(test_plan)
root_node_name = test_plan.get("testname")
# 获取jmx文件根节点
jmx_root = root[0][1]

base_name = balde_root_name + os.path.altsep + root_node_name + os.path.altsep
companents = JmeterElement(test_plan, jmx_root).get_sub_elements()
post_blade = PostBlade()

# 本地保存用户定义变量, 在其他组件中到变量直接替换数据
arguments_local = dict()

for companent in companents:
    if companent.isEnabled():
        # 自定义变量组件处理
        if companent.tag == "Arguments":
            # jmeter转blade测试/iibs/自定义变量
            name = base_name + companent.get("testname")
            logger.info(name)
            deal_arguments(companent, name, arguments_local)
        elif companent.tag == "ThreadGroup":
            logger.info(companent.get("testname"))
            deal_threadgroup(companent, base_name)


