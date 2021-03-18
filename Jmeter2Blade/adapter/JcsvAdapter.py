# -*- coding:utf-8 -*-
# @Time    : 2021/3/18 10:55
# @Author  : zengln
# @File    : JcsvAdapter.py


import xml.etree.ElementTree as ET


tree = ET.parse('movie.xml')
root = tree.getroot()
jmx_root = root[0][1]

for child in jmx_root:
    if child.tag != "hashTree":
        print(child.tag, child.attrib)


if __name__ == "__main__":
    pass