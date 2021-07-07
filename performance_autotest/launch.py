# -*- coding:utf-8 -*-
# @Time    : 2020/12/6 14:29
# @Author  : zengln
# @File    : launch.py

import os
import traceback
import subprocess

from performance_autotest.log import logger
from performance_autotest.customexception import CustomError
from performance_autotest.script import *
from performance_autotest.server import Server
from performance_autotest.resultdata import NmonAnalyse, JmeterAnalyse, LoadRunnerAnalyse
from performance_autotest.report import Report
from performance_autotest.RConfig import Config



class Launch(object):

    # 启动脚本, 包含了压测自动化脚本的主流程

    def __init__(self):
        # 连接后台服务器
        self.servers = []

        # 保存结果文件路径
        self.result_jmeter_file_list = []
        self.result_loadrunner_file_list = []

        # 保存解析文件结果
        self.result_nmon_variable_list = []
        self.result_file_analyse_variable_list = []


    def check_exe(self):
        '''
        检查jmeter是否在运行, 正在运行则退出
        :return:
        '''

        command = "tasklist | findstr java.exe"
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 1:
            if result.stderr:
                raise CustomError(result.stderr.decode('gbk'))
        elif result.returncode == 0:
            command_result_str = result.stdout.decode('gbk')
            logger.debug("命令 %s 执行结果 %a" % (command, command_result_str))
            command_result_list = command_result_str.split(os.linesep)
            logger.debug(command_result_list)
            for command_result in command_result_list:
                if command_result != '':
                    pid = command_result.split()[1]
                    find_jemeter = "jstack %s" % pid
                    result_jm = subprocess.run(find_jemeter, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    if result_jm.returncode == 0:
                        if "jmeter" in result_jm.stdout.decode('gbk'):
                            raise CustomError("jmeter 程序正在运行, 请关闭 jmeter 再开启脚本")
                        else:
                            logger.debug("jmeter不在运行运行")
                    else:
                        if result_jm.stderr:
                            raise CustomError(result_jm.stderr.decode('gbk'))

    def check_dir(self, path):
        logger.debug("检查下载路径是否存在")
        if not os.path.exists(path):
            logger.info("下载路径不存在,创建下载路径")
            os.makedirs(path)

        logger.debug("下载路径检查完成")

    def servers_connect(self):
        logger.info("====开始连接后台服务器====")
        num = int(self.config.remote_host_num)
        for server_index in range(0, num):
            # ip 判空
            if self.config.__getattribute__("ip" + str(server_index)) == "":
                continue

            if self.config.__getattribute__("nmon_path" + str(server_index)) == "":
                server = Server(self.config.__getattribute__("ip" + str(server_index)))
            else:
                server = Server(self.config.__getattribute__("ip" + str(server_index)),
                                self.config.__getattribute__("nmon_path" + str(server_index)))

            server.connect(self.config.__getattribute__("user" + str(server_index)),
                           self.config.__getattribute__("passwd" + str(server_index)))

            self.servers.append(server)
        logger.info("====连接服务器结束====")

    def servers_start_nmon_control(self,script_file_name):
        logger.info("====开启后台监控====")
        num = int(self.config.remote_host_num)
        for server_index in range(0, num):
            self.servers[server_index].start_nmon_control(self.config, script_file_name)

    def servers_close(self):
        logger.info("====关闭后台服务器连接====")
        num = int(self.config.remote_host_num)
        for server_index in range(0, num):
            self.servers[server_index].download_nmon_files(self.config)
            self.servers[server_index].close()

        logger.info("====后台服务器完全关闭====")

    def analyse_nmon(self,server_list, nmon_result_list):
        logger.info("开始解析nmon文件")

        for server in server_list:
            for filepath in server.file_list:
                nmon = NmonAnalyse()
                nmon.set_ip(server.server_name)
                nmon.file_analyse(filepath)
                nmon_result_list.append(nmon)

        logger.info("解析nmon文件结束")

    def analyse_jmeter(self,jmeter_file_list, jmeter_result_list):
        logger.info("开始解析jmeter文件")

        for jmeter_file in jmeter_file_list:
            jmeter = JmeterAnalyse()
            try:
                jmeter.file_analyse(jmeter_file)
            except Exception as e:
                logger.error(e)
                continue
            jmeter_result_list.append(jmeter)

        logger.info("解析jmeter文件结束")

    def analyse_loadrunner(self,loadrunner_file_list, loadrunner_result_list):
        logger.info("开始解析loadrunner文件")

        for loadrunner_file in loadrunner_file_list:
            loadrunner = LoadRunnerAnalyse()
            try:
                loadrunner.file_analyse(loadrunner_file)
            except Exception as e:
                logger.error(e)
                continue
            loadrunner_result_list.append(loadrunner)

        logger.info("解析loadrunner文件结束")

    def check_jmeter_config_param(self):
        # 检查jmeter参数会否填写
        if self.config.jmeter_script_dir == "":
            raise CustomError("JMETER_SCRIPT_DIR 参数不允许为空")

        if self.config.run_in_win == "0":
            if self.config.jmeter_ip == "":
                raise CustomError("参数 jmeter ip 不允许为空")
            elif self.config.jmeter_user == "":
                raise CustomError("参数 jmeter user 不允许为空")
            elif self.config.jmeter_passwd == "":
                raise CustomError("参数 jmeter passwd 不允许为空")

    def check_loadrunner_config_param(self):
        if self.config.loadrunner_script_dir == "":
            raise CustomError("LOADRUNNER_SCRIPT_DIR 参数不允许为空")
        if self.config.run_in_win == "0":
            raise CustomError("Loadrunner 压测方式暂不支持脚本在非 WINDOWS 机器上运行")

    def start(self):
        logger.error("*****************************************************")
        self.config = Config.get_instance()
        self.check_dir(self.config.download_local_path)

        # 生成脚本运行命令
        if self.config.type == "1":
            # 判断参数是否填写
            self.check_jmeter_config_param()
            # jmeter 生成脚本命令前, 检查 jmeter 程序是否存在
            self.check_exe()
            script_path = self.config.jmeter_script_dir
            script_file, path = get_all_script(script_path, ".jmx")
            script_command, result_jmeter_file_list = jmeter_cmd(script_file, path)
        elif self.config.type == "2":
            self.check_loadrunner_config_param()
            script_path = self.config.loadrunner_script_dir
            script_file, path = get_all_script(script_path, ".lrs")
            script_command, result_analyse_command, result_loadrunner_file_list = lr_cmd(script_file, path)
        else:
            raise CustomError("参数type值只能为1或者2,目前值 %s 非法" % self.config.type)

        # 连接后台服务器,运行脚本,开启监控
        self.servers_connect()
        for command in script_command:
            index = script_command.index(command)
            self.servers_start_nmon_control(script_file[index])
            exe_command(command)

        # 下载nmon文件,关闭后台连接
        self.servers_close()

        # 如果是loadrunner需要额外调用命令,解析文件
        if not self.config.loadrunner_script_dir == "" and self.config.jmeter_script_dir == "":
            if len(result_analyse_command) == 0:
                raise CustomError("无法获取 loadrunner 解析命令")
            for command in result_analyse_command:
                exe_command(command)

        self.analyse_nmon(self.servers, self.result_nmon_variable_list)
        if not self.config.jmeter_script_dir == "":
            if len(result_jmeter_file_list) == 0:
                raise CustomError("jmeter 解析时出现异常,找不到结果文件所在路径")
            self.analyse_jmeter(result_jmeter_file_list, self.result_file_analyse_variable_list)
        elif not self.config.loadrunner_script_dir == "":
            if len(result_loadrunner_file_list) == 0:
                raise CustomError("loadrunner 解析时出现异常,找不到结果文件所在路径")
            self.analyse_loadrunner(result_loadrunner_file_list, self.result_file_analyse_variable_list)
        else:
            raise CustomError("脚本路径不能全为空,解析结果失败")

        report = Report()
        report.get_report(self.result_file_analyse_variable_list, self.result_nmon_variable_list,
                          file_name=self.config.report_name,
                          file_path=self.config.report_path)
