# -*- coding:utf-8 -*-
# @Time    : 2021/3/18 10:55
# @Author  : zengln
# @File    : JcsvAdapter.py

import os
import xml.etree.ElementTree as ET

from Jmeter2Blade.socket.PostBlade import VariableData, PostBlade, dealScriptData
from Jmeter2Blade.util.log import logger
from Jmeter2Blade.util.JmeterElement import JmeterElement
from Jmeter2Blade.util.util import random_uuid

post_blade = PostBlade()


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


# 自定义变量组件处理
def deal_arguments(root, node_name):
    variable_date = VariableData(node_name)
    for child in root[0]:
        data = {}
        for sub_child in child:
            if sub_child.attrib['name'] == "Argument.name":
                data["varName"] = sub_child.text
            elif sub_child.attrib['name'] == "Argument.value":
                data["varContent"] = sub_child.text
            elif sub_child.attrib['name'] == "Argument.desc":
                data["variableRemark"] = sub_child.text
        variable_date.set_data(data)

    logger.info(post_blade.dealVariableData(variable_date))


# HTTP 请求组件处理
def deal_HTTPSampler(root, step_name, script_content):
    # 报文提取
    step = dict()
    step["stepName"] = step_name
    step["stepDes"] = root.get("testname")
    # 0—前置，1-后置，2-空
    step["precisionTest"] = "1"
    pre_sqls = list()
    step["preSqlContent"] = pre_sqls
    step["scriptContent"] = script_content

    request_body = root.element.find(".//stringProp[@name='Argument.value']").text
    sub_elements = root.get_sub_elements()
    for sub_element in sub_elements:
        # 前置提取
        if sub_element.get("testname") == "JDBC 预处理程序":
            sql = sub_element.element.find(".//stringProp[@name='query']").text
            logger.info(sql)
            pre_sql = {
                    "id": "",
                    "type": "",
                    "content": "%s" % sql
                    }
            pre_sqls.append(pre_sql)
        # 后置提取
        # 验证提取
        elif sub_element.get("testname") == "响应断言":
            match_string = sub_element.element.find(".//collectionProp[@name='Asserion.test_strings']")[0].text
            step[""] = Josn2Blade(eval(request_body), [], 0, match_string)


# 线程组组件
def deal_threadgroup(root, name):
    logger.info(name)
    sub_elements = root.get_sub_elements()
    for sub_element in sub_elements:
        if sub_element.tag == "HTTPSamplerProxy":
            path = sub_element.element.find(".//stringProp[@name='HTTPSampler.path']").text
            # 先添加脚本
            # ds = dealScriptData(name)
            # ds.set_data_with_default(root.get("testname"), "iibs_config", path, root.get("testname"))
            # _, script_id = post_blade.dealScriptData(ds)
            # 再添加用例数据
            script_id = "1"
            deal_HTTPSampler(sub_element, "步骤1", script_id)
            # request_body = sub_element.element.find(".//stringProp[@name='Argument.value']").text



# 定义blade根路径
root_name = "jmeter转blade测试"
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

companents = JmeterElement(test_plan, jmx_root).get_sub_elements()

for companent in companents:
    if companent.isEnabled():
        # 自定义变量组件处理
        if companent.tag == "Arguments":
            # jmeter转blade测试/iibs/自定义变量
            name = root_name + os.path.altsep + root_node_name + os.path.altsep + companent.get("testname")
            logger.info(name)
            # deal_arguments(child, node_name=name)
        elif companent.tag == "ThreadGroup":
            logger.info(companent.get("testname"))
            base_name = root_name + os.path.altsep + root_node_name
            deal_threadgroup(companent, base_name)


