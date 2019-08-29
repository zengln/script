# -*- coding:utf-8 -*-
# @Time    : 2019/8/27 9:58
# @Author  : zengln
# @File    : start.py

import os
import traceback
import time

from performance_autotest.customexception import CustomError
from performance_autotest.script import *
from performance_autotest.RConfig import config
from performance_autotest.server import Server
from performance_autotest.log import logger

"""
    入口脚本
"""
# TODO 下载监控文件
# TODO 解析监控文件、结果文件
# TODO 提取数据
# TODO 生成简易报告


def check_dir(path):
    logger.debug("检查下载路径是否存在")
    if not os.path.exists(path):
        logger.info("下载路径不存在,创建下载路径")
        os.makedirs(path)

    logger.debug("下载路径检查完成")


def servers_connect(server_list):
    logger.info("====开始连接后台服务器====")
    num = int(config.remote_host_num)
    for server_index in range(0, num):
        if config.__getattribute__("nmon_path" + str(server_index)) == "":
            server = Server(config.__getattribute__("ip" + str(server_index)))
        else:
            server = Server(config.__getattribute__("ip" + str(server_index)),
                            config.__getattribute__("nmon_path" + str(server_index)))

        server.connect(config.__getattribute__("user" + str(server_index)),
                       config.__getattribute__("passwd" + str(server_index)))

        server_list.append(server)
    logger.info("====连接服务器结束====")


def servers_start_nmon_control(script_file_name):
    logger.info("====开启后台监控====")
    num = int(config.remote_host_num)
    for server_index in range(0, num):
        servers[server_index].start_nmon_control(config, script_file_name)


def servers_close(server_list):
    logger.info("====关闭后台服务器连接====")
    num = int(config.remote_host_num)
    for server_index in range(0, num):
        server_list[server_index].download_nmon_files(config)
        server_list[server_index].close()

    logger.info("====后台服务器完全关闭====")


try:
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
    for command in script_command:
        # exe_command(command)
        index = script_command.index(command)
        servers_start_nmon_control(script_file[index])

    servers_close(servers)
except Exception:
    error_msg = traceback.format_exc()
    logger.error(error_msg)
    time.sleep(1)
    input("按任意键退出")
