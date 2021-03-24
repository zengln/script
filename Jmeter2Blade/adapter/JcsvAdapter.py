# -*- coding:utf-8 -*-
# @Time    : 2021/3/18 10:55
# @Author  : zengln
# @File    : JcsvAdapter.py

import os
import xml.etree.ElementTree as ET

from Jmeter2Blade.socket.PostBlade import VariableData, PostBlade
from Jmeter2Blade.util.log import logger
from Jmeter2Blade.util.JmeterElement import JmeterElement


# 自定义变量组件处理
def deal_arguments(root, node_name):
    post_blade = PostBlade()
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


# 线程组组件
def deal_threadgroup(root, name):
    sub_elements = root.get_sub_elements()
    for sub_element in sub_elements:
        if sub_element.tag == "HTTPSamplerProxy":
            request_body = sub_element.element.find(".//stringProp[@name='Argument.value']").text




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
            name = root_name + os.path.altsep + root_node_name + os.path.altsep + companent.get("testname")
            deal_threadgroup(companent, name)


