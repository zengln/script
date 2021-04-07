# -*- coding:utf-8 -*-
# @Time    : 2021/3/24 15:16
# @Author  : zengln
# @File    : JmeterElement.py

from .log import logger
from distutils.util import strtobool

class JmeterElement:
    """
    Jmeter 组件, 包含两部分, 组件实际内容主体和子组件
    Jmeter 组件, 主体放在对应的 XML 结构中
    子组件, 放在与主体平级的 hashTree 结构体下
    """
    element = None
    hash_tree = None

    def __init__(self, element, hash_tree):
        self.element = element
        self.hash_tree = hash_tree
        self.tag = self.element.tag

    def get_sub_elements(self):
        """
        获取所有的子组件
        :return:
        """
        sub_elements = []
        child_nums = len(self.hash_tree)

        for child_index in range(0, child_nums, 2):
            sub_element = JmeterElement(self.hash_tree[child_index], self.hash_tree[child_index + 1])
            sub_elements.append(sub_element)

        return sub_elements

    def has_sub_elements(self):
        '''
        判断是否有子组件
        :return:
        '''
        if len(self.get_sub_elements()) == 0:
            return False
        return True

    def isEnabled(self):
        """
        判断组件是否启用
        :return:True  - 启用
                False - 禁用
        """
        return strtobool(self.element.get("enabled", "false"))

    def get(self, key):
        """
        获取主体组件属性
        :return: 返回属性值
        """
        return self.element.get(key)
