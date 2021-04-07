# -*- coding:utf-8 -*-
# @Time    : 2021/4/6 9:46
# @Author  : zengln
# @File    : zxyAdapter.py

import os
import xml.etree.ElementTree as ET
import re

from Jmeter2Blade.socket.PostBlade import VariableData, PostBlade, dealScriptData, importOfflineCase, importOfflineCase_step
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
    # 传入了验证字段, 则 0 特殊处理
    if check_Message and num == 0:
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
    for child in root.element[0]:
        data = dict()

        var_name = child.find(".//stringProp[@name='Argument.name']")
        if var_name is not None:
            if var_name.text.startswith("varc_"):
                data["varName"] = var_name.text
            else:
                # 将本地变量转成blade格式
                data["varName"] = "varc_" + var_name.text

        var_content = child.find(".//stringProp[@name='Argument.value']")
        if var_content is not None:
            data["varContent"] = var_content.text

        variable_remark = child.find(".//stringProp[@name='Argument.desc']")
        if variable_remark is not None:
            data["variableRemark"] = variable_remark.text

        variable_date.set_data(data)

    resp = post_blade.dealVariableData(variable_date)
    # logger.info(resp)
    if resp is not None:
        logger.error(resp)


# 将text中的jmeter变量替换成blade变量
def replace_argument(text):
    argument_re = re.compile(r'\${(.*?)}', re.S)
    arguments = re.findall(argument_re, text)
    for argument in arguments:
        # 不替换 jmeter 自带变量
        if argument.startswith("__"):
            continue

        # 变量名称替换为 blade 规则
        if argument.startswith("varc"):
            blade_argument = argument
        else:
            blade_argument = 'varc_' + argument
        jmeter_argument = '${' + argument + '}'
        text = text.replace(jmeter_argument, blade_argument)
    return text


# HTTP 请求组件处理
def deal_HTTPSampler(root, step_name, script_content="", request_body=""):
    check_string = ""
    # 初始化 step 数据
    step = importOfflineCase_step()
    step.set_stepname(step_name)
    step.set_stepdes(root.get("testname"))

    if script_content:
        step.set_scriptcontent(script_content)

    # 没有传入报文内容, 自行获取当前报文内容, 否则使用传入内容，request 特殊处理, 将其中使用的变量替换成blade变量
    if not request_body:
        request_body = root.element.find(".//stringProp[@name='Argument.value']").text
    request_body = replace_argument(request_body)

    # HTTP 的子组件处理
    sub_elements = root.get_sub_elements()
    for sub_element in sub_elements:
        # 组件禁用, 不读取
        if not sub_element.isEnabled():
            continue

        # 前置提取
        if sub_element.tag == "JDBCPreProcessor":
            data_source = sub_element.element.find(".//stringProp[@name='dataSource']").text
            sql_text = sub_element.element.find(".//stringProp[@name='query']").text
            # 对sql做提取
            sqls = re.findall(r"([delete|insert|update|select].*?';)", sql_text)
            logger.info("提取的sql:%s" % str(sqls))
            for sql in sqls:
                sql = replace_argument(sql)
                step.add_presqlcontent(data_sources[data_source], sql)
        # 后置提取
        # 验证提取
        elif sub_element.tag in ("ResponseAssertion", "BeanShellAssertion"):
            check_elements = sub_element.element.findall("collectionProp/stringProp")
            check_string = ""
            for check_element in check_elements:
                messages = check_element.text.replace('"', '').split(":")
                check_string += check_string_root + messages[0] + "=" + messages[1] + ";"

            logger.info(check_string)
    logger.debug(request_body)
    step.set_dataarrcontent(Josn2Blade(eval(request_body), [], 0, check_string))

    logger.debug(step)
    return step.get_step()


# 固定定时器组件处理
def deal_constanttimer(root, step_name, script_content):
    step = importOfflineCase_step()
    step.set_default_dataarrcontent()
    step.set_stepname(step_name)
    step.set_stepdes(root.get("testname"))
    step.set_scriptcontent(script_content)
    return step.get_step()


# JDBC 组件处理
def deal_JDBCSample(root):
    step = importOfflineCase_step()
    step.set_stepname(root.get("testname"))
    step.set_default_dataarrcontent()
    step.set_stepdes(root.get("testname"))

    sql = replace_argument(root.element.find(".//stringProp[@name='query']").text)
    logger.info(sql)

    data_source = root.element.find(".//stringProp[@name='dataSource']").text

    sub_elements = root.get_sub_elements()

    for sub_element in sub_elements:
        if sub_element.tag == "ResponseAssertion":
            check_values = sub_element.element.findall("collectionProp/stringProp")
            logger.info(check_values)
            check_keys = re.findall(r'select(.*?)from', sql)[0].strip().split(",")
            check_string = ""
            if len(check_keys) == len(check_values):
                for i in range(len(check_values)):
                    check_string += check_keys[i] + "=" + check_values[i].text
                    if i == len(check_keys) - 1:
                        check_string += ";"
                    else:
                        check_string += "|"
            else:
                check_string = "%s的查询语句的列数与验证个数不相等, 查询语句列数 %s, 验证结果个数%s" \
                               % (root.get("testname"), len(check_keys), len(check_values))
                logger.error(check_string)
        elif sub_element.tag == "JDBCPreProcessor":
            pass

    step.add_checkcontent(check_string, data_sources[data_source], sql)
    return step.get_step()


# 线程组组件
def deal_threadgroup(root, node_path):
    # HTTP 组件
    http_companents = []

    # 线程组名称, 作为用例名称
    thread_group_name = root.get("testname")
    logger.info(node_path)
    sub_elements = root.get_sub_elements()[0].get_sub_elements()

    # 初始化导入用例请求
    ioc = importOfflineCase(node_path)

    # 获取到所有关键组件
    step_num = 0
    steps = []
    for sub_element in sub_elements:
        # 组件为禁用状态, 不读取
        if not sub_element.isEnabled():
            continue

        if sub_element.tag == "HTTPSamplerProxy":
            step_num += 1
            path = sub_element.element.find(".//stringProp[@name='HTTPSampler.path']").text
            script_name = path.split("/")[-1]
            logger.info("script_name:%s" % script_name)
            # 先添加脚本
            ds = dealScriptData(node_path)
            ds.set_data_with_default(script_name, root_url, path)
            resp, script_id = post_blade.dealScriptData(ds)
            # 再添加数据
            steps.append(deal_HTTPSampler(sub_element, "步骤-" + str(step_num), script_id))
        elif sub_element.tag == "ConstantTimer":
            wait_time_text = sub_element.element.find(".//stringProp[@name='ConstantTimer.delay']").text
            wait_time = int(wait_time_text) // 1000
            script_name = "wait_" + str(wait_time) + "s"
            # 新增一个定时延迟的脚本
            ds = dealScriptData(node_path)
            ds.set_wait_with_default(script_name, wait_time, sub_element.get("testname"))
            resp, script_id = post_blade.dealScriptData(ds)
            # 处理定时器
            steps.append(deal_constanttimer(sub_element, "步骤-" + str(step_num), script_id))
        elif sub_element.tag == "JDBCSampler":
            steps.append(deal_JDBCSample(sub_element))

    ioc.add_case(thread_group_name, steps)
    resp = post_blade.importOfflineCase(ioc)
    logger.info(resp)
    if resp is not None:
        logger.error(thread_group_name + resp)

# 根URL, 添加脚本时使用
root_url = "ibps_jmeter_http"
# 检查字符串, 根路径
check_string_root = "bupps_resp_head_"
# 定义blade根路径
balde_root_name = "jmeter转blade测试"

# 本地数据库名称与blade数据库名称映射
data_sources = {
    "ibps": "ibps_jmeter_oracle",
    "test1": "ibps_jmeter_pz",
    "fz": "ibps_jmeter_fz"
}

# 读取xml文件
tree = ET.parse('../jmxfile/网银贷记往账.jmx')

# 获取xml根节点
root = tree.getroot()
# 找到TestPlan组件, 获取blade二级路径名
test_plan = root[0][0]
root_node_name = test_plan.get("testname")
# 获取jmx文件根节点
jmx_root = root[0][1]

base_name = balde_root_name + os.path.altsep + root_node_name + os.path.altsep
companents = JmeterElement(test_plan, jmx_root).get_sub_elements()
post_blade = PostBlade()


for companent in companents:
    if companent.isEnabled():
        # 自定义变量组件处理
        if companent.tag == "Arguments":
            # jmeter转blade测试/iibs/自定义变量
            name = base_name + companent.get("testname")
            logger.info(name)
            deal_arguments(companent, name)
        elif companent.tag == "ThreadGroup":
            logger.info(companent.get("testname"))
            if companent.has_sub_elements():
                deal_threadgroup(companent, base_name)
