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
    data_chose_row = random_uuid(32)
    # 传入了验证字段, 则 0 特殊处理
    if check_Message and num == 0:
        one = [random_uuid(32), "序号", "期望"]
        two = [random_uuid(32), "参数说明", ""]
        three = [data_chose_row, "", check_Message]
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
            temp["sheet" + str(num)][0].append(key+"(Object)")
            temp["sheet" + str(num)][-1].append("sheet"+str(num+dict_num)+"|1")
            Josn2Blade(value, result, num+dict_num)
        else:
            temp["sheet"+str(num)][0].append(key)
            temp["sheet"+str(num)][-1].append(value)

    return data_chose_row, result


# CSV 文件处理
def deal_csv_file(filename):
    '''
    读取csv文件, 获取报文内容, 用例名称和验证结果
    返回一个包含所有用例数据的列表, 列表格式如下
    messages = [
        {"casename": , 用例名称
          "body": ,    报文内容
          "case_side_type":, 正反例类型
          "check_message": 验证结果字符串
        },
        {"casename": , 用例名称
          "body": ,    报文内容
          "case_side_type":, 正反例类型
          "check_message": 验证结果字符串
        }
    ]

    :param filename: 待读取的 csv 文件
    :return: 包含所有用例数据的列表
    '''
    # 给的脚本里文件绝对路径与本机不同
    # 所有只需要脚本名称, 直接从项目的路径下取文件
    logger.info(filename)
    csv_file = open(r"../file/"+filename, encoding="utf8")
    # 数据长度不一定, 通过 yq_respCode 字段定位报文结束位置
    message_stop_index = 0
    titles = csv_file.readline().split(",")
    for title in titles:
        if title in ("yq_respMsg", "yq_respmsg"):
            message_stop_index = titles.index(title) + 1
            break

    messages = []
    for line in csv_file.readlines():
        temp = dict()
        message = dict()
        data = line.split(",")[0:message_stop_index]
        logger.info(data)
        for i in range(1, len(data) - 2):
            temp[titles[i]] = data[i]

        message["casename"] = data[0]
        # 获取正反用例类型
        if "正例" in data[0]:
            message["case_side_type"] = "0"
        else:
            message["case_side_type"] = "1"
        message["check_message"] = check_msg_head + 'respCode=' + data[-2] + ';' + check_msg_head + 'respMsg=' + data[-1] + ';'
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
            # 将本地变量转成blade格式
            data["varName"] = "varc_" + var_name.text

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


# JDBC 组件处理
def deal_JDBCSample(root):
    sqls = root.element.find(".//stringProp[@name='query']").text
    logger.info(sqls)
    step = dict()
    step_json = dict()
    step["stepName"] = root.get("testname")
    step["stepJson"] = step_json
    # 0—前置，1-后置，2-空
    step_json["precisionTest"] = "2"
    step_json["scriptContent"] = ""
    dataContent = dict()
    dataContent["dataArrContent"] = list()
    dataContent["id"] = ""
    dataContent["dataChoseRow"] = ""
    dataContent["content"] = ""
    step_json["dataContent"] = dataContent
    step_json["stepDes"] = root.get("testname")
    pre_sqls = list()
    pre_sql = {
        "connection": connection,
        "id": "",
        "type": "2",
        "content": "%s" % sqls
    }
    pre_sqls.append(pre_sql)
    step_json["preSqlContent"] = pre_sqls
    return step


# HTTP 请求组件处理
def deal_HTTPSampler(root, step_name, script_content, request_body="", check_message=""):
    check_string = ""
    # 报文提取
    step = dict()
    step_json = dict()
    data_content = dict()
    step["stepName"] = step_name
    step["stepJson"] = step_json
    step_json["dataContent"] = data_content
    step_json["stepDes"] = root.get("testname")
    # 0—前置，1-后置，2-空
    step_json["precisionTest"] = "2"
    pre_sqls = list()
    step_json["preSqlContent"] = pre_sqls
    step_json["scriptContent"] = script_content
    # 没有传入报文内容, 自行获取当前报文内容, 否则使用传入内容
    if not request_body:
        request_body = root.element.find(".//stringProp[@name='Argument.value']").text

    # request 特殊处理, 将其中使用的变量替换成blade变量
    argument_re = re.compile(r'\${(.*?)}', re.S)
    arguments = re.findall(argument_re, request_body)
    for argument in arguments:
        # 不替换 jmeter 自带变量
        if argument.startswith("__"):
            continue
        # 变量的写法可能是 ${test}, '${test}', "${test}"
        # 三种都替换
        jmeter_argument = '"${' + argument + '}"'
        blade_argument = '"varc_' + argument + '"'
        request_body = request_body.replace(jmeter_argument, blade_argument)
        jmeter_argument = "'${' + argument + '}'"
        request_body = request_body.replace(jmeter_argument, blade_argument)
        jmeter_argument = '${' + argument + '}'
        request_body = request_body.replace(jmeter_argument, blade_argument)

    sub_elements = root.get_sub_elements()
    for sub_element in sub_elements:
        # 前置提取
        if sub_element.tag == "JDBCPreProcessor":
            sql = sub_element.element.find(".//stringProp[@name='query']").text
            logger.info(sql)
            pre_sql = {
                    "connection": connection,
                    "id": "",
                    "type": "2",
                    "content": "%s" % sql
                    }
            pre_sqls.append(pre_sql)
        # 后置提取
        # 验证提取
        elif sub_element.tag in ("ResponseAssertion", "BeanShellAssertion"):
            logger.debug(check_message)
            check_string = check_message
    logger.debug(request_body)
    data_content["dataChoseRow"], data_content["dataArrContent"] = Josn2Blade(eval(request_body), [], 0, check_string)
    data_content["id"] = ""
    data_content["content"] = ""

    logger.debug(step)
    return step


# 线程组组件
def deal_threadgroup(root, node_path):
    # HTTP 组件
    http_companents = []

    # 线程组名称, 作为用例节点的父级目录名称
    thread_group_name = root.get("testname")
    logger.info(node_path)
    sub_elements = root.get_sub_elements()

    # 如果是csv格式的,包含了控制器,特殊处理
    if sub_elements[0].tag == "TransactionController":
        sub_elements = sub_elements[0].get_sub_elements()

    # 初始化导入用例请求
    ioc = importOfflineCase(node_path + thread_group_name)

    messages = []
    # 获取到所有关键组件
    for sub_element in sub_elements:
        # 组件为禁用状态, 不读取
        if not sub_element.isEnabled():
            continue

        # 从 Beanshell 中将读取的csv文件key取出
        if sub_element.tag in ("BeanShellSampler", "BeanShellPreProcessor") and not messages:
            if sub_element.tag == "BeanShellSampler":
                java_code = sub_element.element.find(".//stringProp[@name='BeanShellSampler.query']").text
            else:
                java_code = sub_element.element.find(".//stringProp[@name='script']").text
            # 获取csv 路径 key
            csv_re = re.compile(r'FileInputStream[(]vars.get[(]"(.*?)"[)]', re.S)
            csv_key = re.findall(csv_re, java_code)[0]
            file_path = arguments_local[csv_key]
            filename = file_path.split("/")[-1]
            logger.info(thread_group_name + "的 csv 文件名称" + filename)
            messages = deal_csv_file(filename)
            logger.info("读取csv文件内容结束")
            logger.info(messages)
        elif sub_element.tag == "Arguments":
            # copp 自定义变量里直接放的文件名, 直接获取报文内容, 无需将变量上送到blade
            csv_file_path = sub_element.element.find(".//stringProp[@name='Argument.value']").text
            csv_file_name = csv_file_path.split("/")[-1]
            logger.info(thread_group_name + "的 csv 文件名称" + csv_file_name)
            messages = deal_csv_file(csv_file_name)
            logger.info("读取csv文件内容结束")
            logger.info(messages)
        elif sub_element.tag == "HTTPSamplerProxy":
            # 在这里改成将 HTTP 组件保存下来, 在后面循环遍历 Message, 重复发送
            http_companents.append(sub_element)
        elif sub_element.tag == "JDBCSampler":
            # JDBC 组件处理
            step = deal_JDBCSample(sub_element)
            ioc.add_case(sub_element.get("testname"), [step])

    # 改到这里发HTTP请求
    if messages:
        # 不为空
        for message in messages:
            step_num = 0
            steps = []
            for http_companent in http_companents:
                step_num += 1
                path = http_companent.element.find(".//stringProp[@name='HTTPSampler.path']").text
                logger.info(path)
                # 先添加脚本
                ds = dealScriptData(node_path)
                ds.set_data_with_default(http_companent.get("testname"), root_url, path, thread_group_name)
                resp, script_id = post_blade.dealScriptData(ds)
                # 再添加数据
                request_body_half = http_companent.element.find(".//stringProp[@name='Argument.value']").text
                requst_body = request_body_half.replace("${req_body}", message["body"])
                logger.debug(requst_body)
                steps.append(deal_HTTPSampler(http_companent, "步骤-"+str(step_num), script_id, requst_body,
                                              message["check_message"]))
            ioc.add_case(message["casename"], steps)
    elif http_companents:
        step_num = 0
        steps = []
        for http_companent in http_companents:
            step_num += 1
            path = http_companent.element.find(".//stringProp[@name='HTTPSampler.path']").text
            logger.info(path)
            # 先添加脚本
            ds = dealScriptData(node_path)
            ds.set_data_with_default(http_companent.get("testname"), root_url, path, thread_group_name)
            resp, script_id = post_blade.dealScriptData(ds)
            # 再添加数据
            steps.append(deal_HTTPSampler(http_companent, "步骤-" + str(step_num), script_id))
        ioc.add_case(thread_group_name, steps)
    else:
        pass

    resp = post_blade.importOfflineCase(ioc)
    # logger.info(resp)
    if resp is not None:
        logger.error(thread_group_name + resp)

check_msg_head = "iibs_resp_head_"
# 配置数据库连接
connection = "iibs_jmeter_oracle"
# 根URL, 添加脚本时试用
root_url = "iibs_http"
# 定义blade根路径
balde_root_name = "jmeter转blade测试"
# 读取xml文件
tree = ET.parse('../jmxfile/iibs_abs_jres.jmx')
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


