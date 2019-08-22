# -*- coding:utf-8 -*-

import os


def get_all_script(script_path, file_extension):
    """
    获取当前文件夹下所有指定后缀文件
    :param script_path:    文件夹路径
    :param file_extension: 文件类型
    :return:
    """
    script_files = []
    if not os.path.exists(script_path):
        # TODO 抛出自定义异常,并退出, 将报错信息打印到日志和控制台
        pass
    files = os.listdir(script_path)
    for file in files:
        if not os.path.isfile(script_path + "\\" + file):
            continue
        if os.path.splitext(file)[1] == file_extension:
            script_files.append(os.path.splitext(file)[0])

    if not script_files.__len__():
        # TODO 抛出自定义异常, 路径下无脚本
        raise Exception

    return script_files


if __name__ == '__main__':
    jmeter_path = r'C:\Users\zeng\Desktop\jemter'
    print(get_all_script(jmeter_path, ".jmx"))



