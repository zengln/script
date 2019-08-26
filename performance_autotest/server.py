# -*- coding:utf-8 -*-
# @Time    : 2019/8/23 15:53
# @Author  : zengln
# @File    : server.py

import paramiko

from performance_autotest.RConfig import config
from performance_autotest.customexception import CustomError


class Server(object):
    """
    后台服务类, 提供命令执行,文件下载等接口
    """
    SSH_PORT = 22

    def __init__(self, ip):
        if not isinstance(ip, (str, bytes)):
            raise CustomError("IP 需要是字符串类型或者bytes类型")

        self.server_name = ip

    def connect(self, user, passwd):
        """
        连接后台 server
        :param user:     用户名
        :param passwd:   密码
        """
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

        self.ssh.close()

    def start_nmon_control(self, config):
        """
        开启后台监控
        :param config:config 对象
        :return:
        """
        if not hasattr(self, "ssh"):
            raise CustomError("未与服务端进行连接")

        nmon_cmd = config.nmon_path + "/nmon -f -t " + config.nmon_acquisition_interval+" -c " + config.nmon_all_time
        print(nmon_cmd)

        stdin, stdout, stderr = self.ssh.exec_command(nmon_cmd)

        if stdout.channel.recv_exit_status():
            err_msg = stderr.read().decode("utf-8")
            raise CustomError(err_msg)


if __name__ == "__main__":
    server = Server(config.ip)
    server.connect(config.user, config.passwd)
    server.start_nmon_control(config)
    server.close()
