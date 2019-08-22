# -*- coding:utf-8 -*-

import os
from performance_autotest.customexception import CustomError


def get_all_script(script_path, file_extension):
    """
    获取当前文件夹下所有指定后缀文件
    :param script_path:    文件夹路径
    :param file_extension: 文件类型
    :return:
    """
    script_files = []
    if not os.path.exists(script_path):
        raise CustomError("路径错误,文件夹不存在")

    files = os.listdir(script_path)
    for file in files:
        if not os.path.isfile(script_path + "\\" + file):
            continue
        if os.path.splitext(file)[1] == file_extension:
            script_files.append(os.path.splitext(file)[0])

    if not script_files.__len__():
        raise CustomError("路径下无后缀为%s的脚本文件" % file_extension)

    return script_files


if __name__ == '__main__':
    jmeter_path = r'C:\Users\zengjn\Desktop\jemter'
    print(get_all_script(jmeter_path, ".jmx"))
