# -*- coding:utf-8 -*-
# @Time    : 2019/8/27 9:58
# @Author  : zengln
# @File    : start.py

import os

from performance_autotest.customexception import CustomError
from performance_autotest.script import *
from performance_autotest.RConfig import config
from performance_autotest.server import Server

"""
    入口脚本
"""

# TODO 检查存放监控文件的路径是否存在
# TODO 获取场景
# TODO 连接后台
# TODO 启动场景
# TODO 启动监控
# TODO 所有场景结束
# TODO 下载监控文件
# TODO 解析监控文件、结果文件
# TODO 提取数据
# TODO 生成简易报告


def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


check_dir(config.download_local_path)

if not config.jmeter_script_dir == "":
    script_path = config.jmeter_script_dir
    script_file = get_all_script(script_path, ".jmx")
    script_command = jmeter_cmd(script_file)
elif not config.loadrunner_script_dir == "":
    script_path = config.loadrunner_script_dir
    script_file = get_all_script(script_path, ".lrs")
    script_command = lr_cmd(script_file)
else:
    raise CustomError("脚本路径不能全为空")


server = Server(config.ip)
server.connect(config.user, config.passwd)

for index, command in script_command:
    exe_command(command)
    server.start_nmon_control(config, script_file[index])

server.download_nmon_files(config)
server.close()
