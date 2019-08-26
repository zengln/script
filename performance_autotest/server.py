# -*- coding:utf-8 -*-
# @Time    : 2019/8/23 15:53
# @Author  : zengln
# @File    : server.py

import paramiko

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


if __name__ == "__main__":
    server = Server("127.0.0.1")
    server.connect("test", "test.123")