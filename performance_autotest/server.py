# -*- coding:utf-8 -*-
# @Time    : 2019/8/23 15:53
# @Author  : zengln
# @File    : server.py

import paramiko
import os

from performance_autotest.RConfig import Config
from performance_autotest.customexception import CustomError
from performance_autotest.log import logger


class Server(object):
    """
    后台服务类, 提供命令执行,文件下载等接口
    """
    SSH_PORT = 22

    def __init__(self, ip, taskid, path="."):
        if not isinstance(ip, (str, bytes)):
            raise CustomError("IP 需要是字符串类型或者bytes类型")

        self.server_name = ip
        self.path = path
        self.taskid = taskid
        # 保存下载 nmon 文件全路径
        self.file_list = []

    def connect(self, user, passwd):
        """
        连接后台 server
        :param user:     用户名
        :param passwd:   密码
        """
        logger.debug("正在与" + self.server_name + "建立连接")
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=self.server_name, port=self.SSH_PORT, username=user, password=passwd)
        self.ssh = ssh_client

    def close(self):
        """
        关闭后台连接
        """
        if not hasattr(self, "ssh"):
            raise CustomError("未与服务端进行连接")
        logger.debug("正在关闭" + self.server_name + "的连接")
        self.ssh.close()

    def start_nmon_control(self, config, filename):
        """
        开启后台监控
        :param config:config 对象
        :param filename: nmon 文件名
        :return:
        """
        if not hasattr(self, "ssh"):
            raise CustomError("未与服务端进行连接")

        stdin, stdout, stderr = self.ssh.exec_command("ls -dl " + self.server_name + "/" + self.taskid)
        if stdout.channel.recv_exit_status():
            stdin, stdout, stderr = self.ssh.exec_command("mkdir " + self.server_name + "/" + self.taskid)

            if stdout.channel.recv_exit_status():
                raise CustomError(stderr.read().decode('utf-8'))



        nmon_filename = filename + ".nmon"
        # 获取采集频率
        nmon_data_rate = str(int(int(config.nmon_all_time) / int(config.nmon_acquisition_interval)))
        nmon_cmd = (self.path + "/nmon -F " + self.path + "/" + self.server_name + "/" + self.taskid + "/"
                    + nmon_filename + " -t -s " + config.nmon_acquisition_interval + " -c " + nmon_data_rate)

        logger.debug("正在开启" + self.server_name + "监控,监控结果文件名为:" + nmon_filename)
        logger.debug("监控命令 %s" % nmon_cmd)
        stdin, stdout, stderr = self.ssh.exec_command(nmon_cmd)

        if stdout.channel.recv_exit_status():
            err_msg = stderr.read().decode("utf-8")
            raise CustomError(err_msg)

    def download_nmon_files(self, config):
        if not hasattr(self, "ssh"):
            raise CustomError("未与服务端进行连接")

        download_local_path = config.download_local_path + os.path.sep + self.server_name + os.path.sep + self.taskid
        if not os.path.exists(download_local_path):
            logger.info("正在创建文件夹" + self.server_name)
            os.mkdir(download_local_path)

        trans = self.ssh.get_transport()
        sftp = paramiko.SFTPClient.from_transport(trans)
        files = sftp.listdir_attr(self.path + "/" + self.server_name + "/" + self.taskid)

        logger.info("开始下载" + self.server_name + "监控文件")
        for file in files:
            logger.debug("正在下载:" + file.filename)
            sftp.get(self.path + "/" + self.server_name + "/" + self.taskid + "/" + file.filename,
                     download_local_path + "\\" + file.filename)
            self.file_list.append(download_local_path + "\\" + file.filename)
        trans.close()
        # --add 20200515 报告显示顺序存在乱序的情况, 在保存完所有的文件路径后, 进行排序
        self.file_list.sort()
        logger.info("%s 监控文件下载完成, 文件保存在 %s" % (self.server_name, download_local_path))

    def get_file_handle_num(self) -> str:
        '''
        获取文件句柄数量
        :return:
        '''

        get_file_handle = "lsof |wc -l"
        return self.exec_command(get_file_handle)

    def exec_command(self, command) -> str:
        stdin, stdout, stderr = self.ssh.exec_command(command)
        if stdout.channel.recv_exit_status():
            err_msg = stderr.read().decode('utf-8')
            raise CustomError(err_msg)
        return stdout.read().decode('utf-8')


if __name__ == "__main__":
    config = Config.get_instance()
    server = Server(config.ip0)
    server.connect(config.user0, config.passwd0)
    print(server.get_file_handle_num())
    server.close()
