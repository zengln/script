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
# TODO 启动监控(需要支持集群)
# TODO 所有场景结束
# TODO 下载监控文件
# TODO 解析监控文件、结果文件
# TODO 提取数据
# TODO 生成简易报告


def check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def servers_connect(server_list):
    num = int(config.remote_host_num)
    for server_index in range(0, num):
        server = Server(config.__getattribute__("ip" + str(server_index)))
        server.connect(config.__getattribute__("user" + str(server_index)),
                       config.__getattribute__("passwd" + str(server_index)))
        server_list.append(server)


def servers_start_nmon_control(script_file_name):
    num = int(config.remote_host_num)
    for server_index in range(0, num):
        servers[server_index].start_nmon_control(config, script_file_name)


def servers_close(server_list):
    num = int(config.remote_host_num)
    for server_index in range(0, num):
        server_list[server_index].download_nmon_files(config)
        server_list[server_index].close()


check_dir(config.download_local_path)

if not config.jmeter_script_dir == "":
    script_path = config.jmeter_script_dir
    script_file = get_all_script(script_path, ".jmx")
    script_command = jmeter_cmd(script_file, config.jmeter_script_dir)
elif not config.loadrunner_script_dir == "":
    script_path = config.loadrunner_script_dir
    script_file = get_all_script(script_path, ".lrs")
    script_command = lr_cmd(script_file, config.loadrunner_script_dir)
else:
    raise CustomError("脚本路径不能全为空")

servers = []
servers_connect(servers)

for index, command in script_command:
    exe_command(command)
    servers_start_nmon_control(script_file[index])

servers_close(servers)
