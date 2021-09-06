# -*- coding:utf-8 -*-
# @Time    : 2021/9/6 9:06
# @Author  : zengln
# @File    : ecsAdapter.py

import os
import xml.etree.ElementTree as ET
import re

from pathlib import Path
from Jmeter2Blade.socket.PostBlade import VariableData, PostBlade, dealScriptData, importOfflineCase, \
    importOfflineCase_step
from Jmeter2Blade.util.log import logger
from Jmeter2Blade.util.JmeterElement import JmeterElement
from Jmeter2Blade.util.util import random_uuid

count = 0


def Josn2Blade(message, result, num=0, check_Message=""):
    """
    将报文转化为Blade可接收的测试数据格式
    :param message: 报文数据
    :param num: sheet计数
    :param result: Blade 数据格式
    :param check_Message: 验证字符串
    :return:
    """
    temp = dict()
    temp["sheet" + str(num)] = []
    result.append(temp)
    dict_num = 0
    data_chose_row = random_uuid(32)
    # 传入了验证字段, 则 0 特殊处理
    if num == 0:
        one = [random_uuid(32), "序号", "期望"]
        two = [random_uuid(32), "参数说明", ""]
        three = [data_chose_row, "", check_Message]
        temp["sheet" + str(num)].append(one)
        temp["sheet" + str(num)].append(two)
        temp["sheet" + str(num)].append(three)
    else:
        one = [random_uuid(32), "GroupID"]
        two = [random_uuid(32), "1"]
        temp["sheet" + str(num)].append(one)
        temp["sheet" + str(num)].append(two)

    for key, value in message.items():
        if isinstance(value, dict):
            dict_num += 1
            temp["sheet" + str(num)][0].append(key + "(Object)")
            temp["sheet" + str(num)][-1].append("sheet" + str(num + dict_num) + "|1")
            Josn2Blade(value, result, num + dict_num)
        else:
            temp["sheet" + str(num)][0].append(key)
            temp["sheet" + str(num)][-1].append(value)

    return data_chose_row, result


# 将text中的jmeter变量替换成blade变量
def replace_argument(text):
    argument_re = re.compile(r'\${(.*?)}', re.S)
    arguments = re.findall(argument_re, text)
    for argument in arguments:
        # 不替换 jmeter 自带变量
        if argument.startswith("__"):
            continue

        jmeter_argument = '${' + argument + '}'
        # 变量名称替换为 blade 规则
        if argument.startswith("varc"):
            blade_argument = argument
        else:
            blade_argument = 'varc_' + argument

        # 替换掉 var_name_1 -> var_name
        temp_list = re.findall(r'(.*?)_[0-9]{1}', blade_argument)
        if temp_list:
            blade_argument = temp_list[0]

        text = text.replace(jmeter_argument, blade_argument)
    return text


# 检查变量名称是否按照blade规则命名
def check_argument(argument):
    if not argument.startswith("varc_"):
        argument = "varc_" + argument
    return argument


# 自定义变量组件处理
def deal_arguments(root, node_name):
    variable_date = VariableData(node_name)
    for child in root.element[0]:
        data = dict()

        var_name = child.find(".//stringProp[@name='Argument.name']")
        if var_name is not None:
            data["varName"] = check_argument(var_name.text)

        var_content = child.find(".//stringProp[@name='Argument.value']")
        if var_content is not None:
            data["varContent"] = var_content.text

        variable_remark = child.find(".//stringProp[@name='Argument.desc']")
        if variable_remark is not None:
            data["variableRemark"] = variable_remark.text

        arguments_local[var_name.text] = var_content.text
        variable_date.set_data(data)

    resp = post_blade.dealVariableData(variable_date)
    # logger.debug(resp)
    if resp is not None:
        logger.error("添加自定义变量失败, 原因:{}".format(resp))
    else:
        logger.info("添加自定义变量成功")
    global count
    logger.info(count)
    count += 1


def deal_transaction_controller(root, node_path):
    steps = []

    sub_elements = root.get_sub_elements()
    # 获取到所有关键组件
    step_num = len(steps)
    for sub_element in sub_elements:
        # 组件为禁用状态, 不读取
        if not sub_element.isEnabled():
            continue

        if sub_element.tag == "HTTPSamplerProxy":
            step_num += 1
            path = sub_element.element.find(".//stringProp[@name='HTTPSampler.path']").text
            script_name = path.split("/")[-1]
            logger.debug("script_name:%s" % script_name)
            # 先添加脚本
            ds = dealScriptData(node_path)
            ds.set_data_with_default(script_name, root_url, path)
            resp, script_id = post_blade.dealScriptData(ds)
            # 再添加数据
            steps.append(deal_HTTPSampler(sub_element, "步骤-" + str(step_num), script_id))
        elif sub_element.tag == "JDBCSampler":
            steps += deal_JDBCSample(sub_element)
    return steps


# 自定义变量组件处理
def deal_arguments(root, node_name):
    variable_date = VariableData(node_name)
    for child in root.element[0]:
        data = dict()

        var_name = child.find(".//stringProp[@name='Argument.name']")
        if var_name is not None:
            data["varName"] = check_argument(var_name.text)

        var_content = child.find(".//stringProp[@name='Argument.value']")
        if var_content is not None:
            data["varContent"] = var_content.text

        variable_remark = child.find(".//stringProp[@name='Argument.desc']")
        if variable_remark is not None:
            data["variableRemark"] = variable_remark.text

        arguments_local[var_name.text] = var_content.text
        variable_date.set_data(data)

    resp = post_blade.dealVariableData(variable_date)
    # logger.debug(resp)
    if resp is not None:
        logger.error("添加自定义变量失败, 原因:{}".format(resp))
    else:
        logger.info("添加自定义变量成功")
    global count
    logger.info(count)
    count += 1


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
            variable_name = sub_element.element.find(".//stringProp[@name='variableNames']").text
            # 对sql做提取
            sqls = re.findall(
                r"([delete|insert|update|select|DELETE|INSERT|UPDATE|SELECT|Update|Insert|Select|Delete].*?'.*;)",
                sql_text)
            logger.debug("提取的sql:%s" % str(sqls))
            for sql in sqls:
                sql = replace_argument(sql)
                if "%" in sql:
                    sql = sql.replace("%", "%25")
                if variable_name:
                    sql = variable_name + "|" + sql
                step.add_presqlcontent(data_sources[data_source], sql)
        # 后置提取
        # 验证提取
        elif sub_element.tag in ("ResponseAssertion", "BeanShellAssertion"):
            check_elements = sub_element.element.findall("collectionProp/stringProp")
            check_string = ""
            for check_element in check_elements:
                if check_element.text:
                    messages = check_element.text.replace('"', '').split(":")
                    if len(messages) == 1:
                        check_string += check_element.text
                    else:
                        check_string += check_string_root + messages[0] + "=" + messages[1] + ";"

            logger.debug(check_string)
    logger.debug(request_body)
    data_chose_row, data_arr_content = Josn2Blade(eval(request_body), [], 0, check_string)
    step.set_dataarrcontent(data_chose_row, data_arr_content)

    logger.debug(step)
    return step.get_step()


def deal_user_parameters(root):
    step = importOfflineCase_step()
    step.set_stepdes(root.get("testname"))
    params_str = ""
    names = root.element.findall("collectionProp[@name='UserParameters.names']/stringProp")
    values = root.element.findall("collectionProp[@name='UserParameters.thread_values']//stringProp")
    for i in range(len(names)):
        params_str += check_argument(names[i].text) + "|" + values[i].text + ";"
    logger.debug(params_str)
    step.add_presqlcontent(data_sources["default"], params_str)
    return step.get_step()


# redis BeanShellSample 组件
def deal_redis_beanshellsampler(root):
    # 添加脚本
    script_name = "redis_jmeter_smart_route"
    ssh_connect = "smart_route_jmeter_redis"
    ds = dealScriptData(base_name)
    ds.set_ssh_with_default(script_name, ssh_connect, root.get("testname"))
    resp, script_id = post_blade.dealScriptData(ds)
    # 添加数据
    data_content = list()
    temp = dict()
    temp["sheet0"] = list()
    data_chose_row = random_uuid(32)
    one = [random_uuid(32), "序号", "期望", "command"]
    two = [random_uuid(32), "参数说明", "", "脚本文件需要事先放到redis的bin目录下"]
    three = [data_chose_row, "", "keyword=OK", "EXEC,sh clear_redis_ecs.sh;"]
    temp["sheet0"].append(one)
    temp["sheet0"].append(two)
    temp["sheet0"].append(three)
    data_content.append(temp)

    step = importOfflineCase_step()
    step.set_stepname(root.tag + root.get("testname"))
    step.set_stepdes(root.get("testname"))
    step.set_scriptcontent(script_id)
    step.set_dataarrcontent(data_chose_row, data_content)
    return step.get_step()


# JDBC 组件处理
def deal_JDBCSample(root):
    step = importOfflineCase_step()
    step.set_stepname(root.get("testname"))
    step.set_stepdes(root.get("testname"))
    steps = [step.get_step()]

    sql_text = replace_argument(root.element.find(".//stringProp[@name='query']").text)
    sqls_list = re.findall(
        r"((delete|insert|update|select|DELETE|INSERT|UPDATE|SELECT|Update|Insert|Select|Delete|Truncate|truncate|TRUNCATE).+[\s\S])",
        sql_text)
    sqls = [sql_list[0] for sql_list in sqls_list]
    logger.debug(sqls)
    data_source = root.element.find(".//stringProp[@name='dataSource']").text
    for sql in sqls:
        if "%" in sql:
            sql = sql.replace("%", "%25")
        logger.debug(sql)
        step.add_presqlcontent(data_sources[data_source], sql)

    sub_elements = root.get_sub_elements()
    # 没有子组件, 纯粹是执行一条sql
    if not sub_elements:
        logger.debug("no sub element")
        return steps

    for sub_element in sub_elements:
        if not sub_element.isEnabled():
            continue

        if sub_element.tag == "BeanShellPostProcessor":
            steps.append(deal_redis_beanshellsampler(sub_element))
        elif sub_element.tag == "BeanShellAssertion":
            check_results = list(sub_element.element.find(".//stringProp[@name='BeanShellAssertion.parameters']").text)
            # 清空presqlcontent, 存在这个子组件,说明JDBC里存放的是验证SQL
            step.set_presqlcontent(list())
            for i in range(len(sqls)):
                check_string = "count(1)={};".format(check_results[i])
                sql = sqls[i]
                logger.debug("check sql:{}, check:{}".format(sql, check_string))
                step.add_checkcontent(check_string, data_sources[data_source], sql)

    return steps


# 线程组组件
def deal_threadgroup(root, node_path):
    # 线程组名称, 作为用例名称
    thread_group_name = root.get("testname")
    logger.debug(node_path)
    sub_elements = root.get_sub_elements()

    # 初始化导入用例请求
    ioc = importOfflineCase(node_path + thread_group_name)
    # ioc = importOfflineCase(node_path)
    steps = []
    # 获取到所有关键组件
    for sub_element in sub_elements:
        # 组件为禁用状态, 不读取
        if not sub_element.isEnabled():
            continue

        if sub_element.tag == "TransactionController":
            # 一个事务控制器, 作为一条用例
            ioc.add_case(sub_element.get("testname"), deal_transaction_controller(sub_element, node_path))
        elif sub_element.tag == "JDBCSampler":
            steps += deal_JDBCSample(sub_element)
    if steps:
        ioc.add_case(thread_group_name, steps)
    resp = post_blade.importOfflineCase(ioc)
    logger.debug(resp)
    if resp is not None:
        logger.error("用例{}添加失败, 原因:{}".format(thread_group_name, resp))
    else:
        logger.info("用例{}添加成功".format(thread_group_name))
    global count
    logger.info(count)
    count += 1


# 根URL, 添加脚本时使用
root_url = "ECS_IAR"
# 检查字符串, 根路径
check_string_root = "bupps_resp_head_"
# 定义blade根路径
balde_root_name = "jmeter转blade测试"

# 本地数据库名称与blade数据库名称映射
data_sources = {
    "ecs": "ecs",
}

# 本地保存用户定义变量, 在其他组件中到变量直接替换数据
arguments_local = dict()
post_blade = PostBlade()

JMX_DIR = Path(__file__).resolve().parent.parent

file_path = JMX_DIR / "file/电子账户/zln/余额支付.jmx"

# 读取xml文件
tree = ET.parse(file_path)

# 获取xml根节点
root = tree.getroot()
# 找到TestPlan组件, 获取blade二级路径名
test_plan = root[0][0]
# root_node_name = test_plan.get("testname")
root_node_name = os.path.splitext(os.path.split(file_path)[1])[0]
# 获取jmx文件根节点
jmx_root = root[0][1]

base_name = balde_root_name + os.path.altsep + root_node_name + os.path.altsep
companents = JmeterElement(test_plan, jmx_root).get_sub_elements()

for companent in companents:
    if not companent.isEnabled():
        continue

    # 自定义变量组件处理
    if companent.tag == "Arguments":
        name = base_name + companent.get("testname")
        logger.info("开始处理自定义变量:{}".format(name))
        deal_arguments(companent, name)
    elif companent.tag == "ThreadGroup":
        logger.info("开始处理用例{}".format(companent.get("testname")))
        if companent.has_sub_elements():
            deal_threadgroup(companent, base_name)
