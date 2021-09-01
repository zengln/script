# -*- coding:utf-8 -*-
# @Time    : 2021/5/20 13:24
# @Author  : zengln
# @File    : znlyAdapter.py

import os
import xml.etree.ElementTree as ET
import re
import json

from pathlib import Path
from Jmeter2Blade.socket.PostBlade import VariableData, PostBlade, dealScriptData, importOfflineCase, \
    importOfflineCase_step
from Jmeter2Blade.util.log import logger
from Jmeter2Blade.util.JmeterElement import JmeterElement
from Jmeter2Blade.util.util import random_uuid

count = 1


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


# 判断变量是否为jmeter变量, 并且返回对应的值
def jmeter_get_argument_value(argument):
    key = re.findall(r'\${(.*?)}', argument)
    if not key:
        return argument
    return arguments_local[key[0]]


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
    three = [data_chose_row, "", "keyword=OK", "EXEC,sh clear_redis_smart_route.sh;"]
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
        r"((delete|insert|update|select|DELETE|INSERT|UPDATE|SELECT|Update|Insert|Select|Delete|Truncate|truncate|TRUNCATE).+[\s\S].+;)",
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
            if "redis" in sub_element.get("testname"):
                steps.append(deal_redis_beanshellsampler(sub_element))

    return steps


# SSH Command 组件处理
def deal_ssh_command(root):
    step = importOfflineCase_step()
    step.set_stepname(root.get("testname"))
    step.set_stepdes(root.get("testname"))
    steps = [step.get_step()]

    # 添加脚本
    script_name = "ssh_jmeter_smart_route"
    ssh_connect = "smart_route_jmeter_ssh"
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
    three = [data_chose_row, "", "keyword=OK",
             "EXEC,sh {};".format(root.element.find(".//stringProp[@name='command']").text)]
    temp["sheet0"].append(one)
    temp["sheet0"].append(two)
    temp["sheet0"].append(three)
    data_content.append(temp)

    step.set_scriptcontent(script_id)
    step.set_dataarrcontent(data_chose_row, data_content)

    return steps


# CSV 文件处理
def deal_csv_file(filename, stop_list=list()):
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
    if not stop_list:
        stop_list = ['yq_respcode', 'yq_respmsg']
        # stop_list = ['ziduanname']
    logger.debug(stop_list)
    # 给的脚本里文件绝对路径与本机不同
    # 所有只需要脚本名称, 直接从项目的路径下取文件
    logger.debug(filename)
    csv_file = open(CSV_FILE_DIR / filename, encoding="gbk")
    # 数据长度不一定, 通过 yq_respCode 字段定位报文结束位置
    titles = csv_file.readline().split(",")
    message_stop_index = len(titles)
    for title in titles:
        if title in stop_list:
            message_stop_index = titles.index(title)
            break
    messages = []
    for line in csv_file.readlines():
        temp = dict()
        message = dict()
        data = line.split(",")[0:message_stop_index]
        check_data = line.split(",")[message_stop_index:message_stop_index + 3]
        logger.debug(data)
        for i in range(1, len(data) - 3):
            temp[titles[i]] = data[i]

        message["casename"] = data[0]
        message["casename"] = message["casename"].replace("<", "").replace(">", "")

        # 获取正反用例类型
        if "正例" in data[0]:
            message["case_side_type"] = "0"
        else:
            message["case_side_type"] = "1"
        # 考虑下没有结果验证的场景
        if len(check_data):
            message["check_message"] = check_msg_head + 'respCode=' + check_data[-3] + ';' + check_msg_head + 'respMsg=' + \
                                       check_data[
                                           -2] + ';' + check_msg_head + 'serviceStatus=' + check_data[-1]
        else:
            message["check_message"] = ""
        message["body"] = json.dumps(temp)
        messages.append(message)

    return messages


# 处理csv特殊线程组
def deal_csv_threadgroup(root):
    sub_elements = root.get_sub_elements()
    http_companents = []
    messages = None
    cases = []
    csv_file_name = None
    for sub_element in sub_elements:
        if not sub_element.isEnabled():
            continue

        if sub_element.tag == "BeanShellPreProcessor":
            script = sub_element.element.find(".//stringProp[@name='script']").text
            logger.debug(re.findall(r'new FileInputStream\(vars.get\("(.*?)"\)\);', script))
            csv_file = re.findall(r'new FileInputStream\(vars.get\("(.*?)"\)\);', script)[0]
            csv_file_path = arguments_local.get(csv_file)
            csv_file_name = os.path.split(csv_file_path)[-1]
            logger.debug(csv_file_name)
            messages = deal_csv_file(csv_file_name)
        elif sub_element.tag == "HTTPSamplerProxy":
            # 在这里改成将 HTTP 组件保存下来, 在后面循环遍历 Message, 重复发送
            http_companents.append(sub_element)
            for sub_sub_element in sub_element.get_sub_elements():
                if sub_sub_element.tag == "BeanShellAssertion":
                    assert_text = sub_sub_element.element.find(".//stringProp[@name='BeanShellAssertion.query']").text
                    results = re.findall(r'vars.get\("(.*?)"\).equals(.*?)', assert_text)
                    stop_list = [result[0] for result in results]
                    messages = deal_csv_file(csv_file_name, stop_list)

    for message in messages:
        step_num = 0
        steps = []
        for http_companent in http_companents:
            step_num += 1
            request_body_half = http_companent.element.find(".//stringProp[@name='Argument.value']").text
            requst_body = request_body_half.replace("${req_body}", message["body"])
            logger.debug(requst_body)
            steps.append(deal_HTTPSampler(http_companent, "步骤-" + str(step_num), requst_body, message["check_message"]))
        cases.append([message["casename"], steps])
    return cases


# HTTP 请求组件处理
def deal_HTTPSampler(root, step_name, request_body="", check_message=""):
    # 没有传入报文内容, 自行获取当前报文内容, 否则使用传入内容
    # 通过获取到的报文参数个数确认是否为json格式或者其他格式
    content_type = None
    if not request_body:
        arguments = root.element.findall(".//elementProp[@elementType='HTTPArgument']")
        if len(arguments) == 1:
            request_body = arguments[0].find(".//stringProp[@name='Argument.value']").text
        else:
            content_type = "application/x-www-form-urlencoded"
            body = dict()
            for argument in arguments:
                key = argument.find(".//stringProp[@name='Argument.name']").text
                value = argument.find(".//stringProp[@name='Argument.value']").text
                body[key] = value
            request_body = str(body)

    # 生成脚本
    path = root.element.find(".//stringProp[@name='HTTPSampler.path']").text
    logger.debug(path)
    # 先添加脚本
    ds = dealScriptData(base_name)
    ds.set_data_with_default(root.get("testname"), root_url, path, content_type=content_type)
    resp, script_content = post_blade.dealScriptData(ds)

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
                # 暂没遇到, 遇到后修改
                "connection": data_sources["test"],
                "id": "",
                "type": "2",
                "content": "%s" % sql
            }
            pre_sqls.append(pre_sql)
        # 后置提取
        # 验证提取
        elif sub_element.tag == "BeanShellAssertion":
            if not check_message:
                assert_text = sub_element.element.find(".//stringProp[@name='BeanShellAssertion.query']").text
                results = re.findall(r'"(.*?)".equals\("(.*?)"\)', assert_text)
                logger.debug(results)
                for result in results:
                    if not results.index(result) == 0:
                        check_message += ";"
                    if "respcode" in result[1].lower():
                        if "UNKNOWN" in result[0].upper():
                            continue
                        check_message += check_msg_head + 'respCode=' + result[0]
                    elif "respmsg" in result[1].lower():
                        check_message += check_msg_head + 'respMsg=' + result[0]
                    elif "servicestatus" in result[1].lower():
                        check_message += check_msg_head + 'serviceStatus=' + result[0]

            check_string = check_message
    logger.debug(request_body)
    data_content["dataChoseRow"], data_content["dataArrContent"] = Josn2Blade(eval(request_body), [], 0, check_string)
    data_content["id"] = ""
    data_content["content"] = ""

    logger.debug(step)
    return step


# 循环控制器
def deal_LoopController(root):
    step = importOfflineCase_step()
    step.set_stepname(root.get("testname"))
    step.set_stepdes(root.get("testname"))
    steps = [step.get_step()]

    sub_elements = root.get_sub_elements()
    for sub_element in sub_elements:
        if sub_element.tag == "BeanShellPreProcessor":
            script = sub_element.element.find(".//stringProp[@name='script']").text
            csv_file = re.findall(r'new FileInputStream\(vars.get\("(.*?)"\)\);', script)[0]
            csv_file_path = arguments_local.get(csv_file)
            csv_file_name = os.path.split(csv_file_path)[-1]
            logger.debug(csv_file_name)
            csv_file = open(CSV_FILE_DIR / csv_file_name, encoding="gbk")
            lines = csv_file.readlines()
            for line in lines:
                line_list = line.split(",")
                after_sqls = line_list[-2]
                results = line_list[-1]
                after_sqls_list = after_sqls.split("union ALL")
                result_list = results.split("|")
                for i in range(len(after_sqls_list)):
                    check_string = "count(1)={};".format(result_list[i])
                    step.add_checkcontent(check_string, data_sources["bupps_107_orcl"], after_sqls_list[i])
    return steps


# 线程组组件
def deal_threadgroup(root, node_path):
    # 线程组名称, 作为用例名称
    csv_flag = False
    thread_group_cases = False
    thread_group_name = root.get("testname")
    logger.debug(node_path)
    sub_elements = root.get_sub_elements()

    # 初始化导入用例请求
    ioc = importOfflineCase(node_path)

    steps = []
    # 检查当前线程组是否使用csv
    for sub_element in sub_elements:
        if not sub_element.isEnabled():
            continue

        if sub_element.tag == "CSVDataSet":
            csv_flag = True
            break
        elif sub_element.tag == "HTTPSamplerProxy" and "正例" in sub_element.get("testname"):
            thread_group_cases = True
            break
        elif sub_element.tag == "CounterConfig":
            # 有计数器,也是一种读取csv的情况
            csv_flag = True
            break

    if csv_flag:
        for sub_element in sub_elements:
            if not sub_element.isEnabled():
                continue

            # if sub_element.tag == "IfController":
            #     root = sub_element

        cases = deal_csv_threadgroup(root)
        for case in cases:
            ioc.add_case(case[0], case[1])
    elif thread_group_cases:
        # 组件为禁用状态, 不读取
        for sub_element in sub_elements:
            if not sub_element.isEnabled():
                continue

            step = None
            if sub_element.tag == "JDBCSampler":
                step = deal_JDBCSample(sub_element)
            elif sub_element.tag == "HTTPSamplerProxy":
                step = [deal_HTTPSampler(sub_element, "步骤一")]
            else:
                continue

            ioc.add_case(sub_element.get("testname"), step)
    else:
        # 获取到所有关键组件
        for sub_element in sub_elements:
            # 组件为禁用状态, 不读取
            if not sub_element.isEnabled():
                continue

            if sub_element.tag == "JDBCSampler":
                steps += deal_JDBCSample(sub_element)
            elif sub_element.tag == "org.apache.jmeter.protocol.ssh.sampler.SSHCommandSampler":
                steps += deal_ssh_command(sub_element)
            elif sub_element.tag == "HTTPSamplerProxy":
                steps += [deal_HTTPSampler(sub_element, sub_element.get("testname"))]
            elif sub_element.tag == "LoopController":
                # 循环控制器检查结果
                steps += deal_LoopController(sub_element)
                pass
            logger.debug(steps)
        ioc.add_case(thread_group_name, steps)

    # resp = None
    resp = post_blade.importOfflineCase(ioc)
    logger.debug(resp)
    if resp is not None:
        logger.error("用例{}添加失败, 原因:{}".format(thread_group_name, resp))
    else:
        logger.info("用例{}添加成功".format(thread_group_name))
    global count
    logger.info(count)
    count += 1


CSV_FILE_DIR = Path(__file__).parent.parent / "file/智能路由/document"
# 根URL, 添加脚本时使用
root_url = "ibps_jmeter_http"
# 检查字符串, 根路径
check_string_root = "bupps_resp_head_"
# 定义blade根路径
balde_root_name = "jmeter转blade测试"

# 本地数据库名称与blade数据库名称映射
data_sources = {
    "bupps": "smart_route_jmeter_oracle"
}

check_msg_head = "bupps_resp_head_"

# 本地保存用户定义变量, 在其他组件中到变量直接替换数据
arguments_local = dict()

# IBM MQ 连接名称
ibm_mq_connect = "ibm_jmeter_mq"

JMX_DIR = Path(__file__).resolve().parent.parent

file_path = JMX_DIR / "file/智能路由/Auto-HuiLuChongFa.jmx"

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
post_blade = PostBlade()

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
