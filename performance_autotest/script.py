# -*- coding:utf-8 -*-

import os

lr_path = r'C:\Users\zengjn22046\Desktop\Get\scenario'
jmeter_path = r'C:\Users\zengjn22046\Desktop\jemter'

cmd_lr = r'C:\"Program Files (x86)"\HP\LoadRunner\bin\wlrun -TestPath  C:\Users\zeng\Desktop\Get\scenario\Scenario-5.lrs -Run -ResultName C:\Users\zeng\Desktop\Get\scenario\res-5'

cmd_jmeter = r'D:\JMeter\apache-jmeter-5.1.1\bin\jmeter -n -t C:\Users\zeng\Desktop\test.jmx -l C:\Users\zeng\Desktop\test.jtl'

# os.system(cmd)
# p = os.popen(cmd_jmeter)
# print(p.read())


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
    lr_path = r'C:\Users\zengjn22046\Desktop\Get\scenario'
    jmeter_path = r'C:\Users\zengjn22046\Desktop\jemter'
    print(get_all_script(lr_path, ".jmx"))



