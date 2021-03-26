# -*- coding:utf-8 -*-
# @Time    : 2021/3/18 10:46
# @Author  : zengln
# @File    : util.py

'''
工具类

后续考虑是否放入配置文件, 工具类不对外开放
'''

TOKEN = ""
account = ""
dealVariableData_url = ""
importOfflineCase_url = ""
dealScriptData_url = ""


def random_uuid(length:int) ->str:
    """
    随机生成一个包含数字字母的指定长度随机字符串
    :param length: 生成随机字符串的长度
    :return: 随机字符串
    """
    import random, string
    return ''.join(random.choice(string.digits + string.ascii_letters) for _ in range(length))


if __name__ == "__main__":
    print(random_uuid(32))