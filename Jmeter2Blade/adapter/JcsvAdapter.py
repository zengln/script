# -*- coding:utf-8 -*-
# @Time    : 2021/3/18 10:55
# @Author  : zengln
# @File    : JcsvAdapter.py

import os
import xml.etree.ElementTree as ET

from Jmeter2Blade.socket.PostBlade import VariableData, PostBlade
from Jmeter2Blade.util.log import logger

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
def deal_threadgroup(root, node_name):
    for child in root:
        # 处理HTTP请求
        if child.tag == "HTTPSamplerProxy":
            # TODO 解析这个组件,组装请求报文
            pass


# 定义blade根路径
root_name = "jmeter转blade测试"
# 读取xml文件
tree = ET.parse('movie.jmx')
# 获取xml根节点
root = tree.getroot()
# 找到TestPlan组件, 获取blade二级路径名
test_plan = root[0].findall('TestPlan')
logger.info(test_plan)
root_node_name = test_plan[0].get("testname")
# 获取jmx文件根节点
jmx_root = root[0][1]
# 记录上一个组件
last_child = None
last_child_enabled = False

for child in jmx_root:
    if child.get("enabled", "false") == "true" or (child.tag == "hashTree" and last_child_enabled):
        # 自定义变量组件处理
        if child.tag == "Arguments":
            # jmeter转blade测试/iibs/自定义变量
            name = root_name + os.path.altsep + root_node_name + os.path.altsep + child.get("testname")
            logger.info(name)
            # deal_arguments(child, node_name=name)
        # 线程组组件处理
        elif child.tag == "ThreadGroup":
            last_child = "ThreadGroup"
            last_name = child.get("testname")
            last_child_enabled = True
        # hashTree 处理, Thread 线程组件中, 实际需要提取的数据信息都放在相邻的 hashTree 中
        elif child.tag == "hashTree":
            last_child_enabled = False
            if last_child == "ThreadGroup":
                name = root_name + os.path.altsep + root_node_name + os.path.altsep + last_name
                deal_threadgroup(child, name)

