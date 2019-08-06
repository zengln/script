# -*- coding:utf-8 -*-

from nmon import ExcelMicro
from nmon import NmonResult
from nmon import RConfig
from nmon import SSHSokcet
import traceback
import os
import sys


def get_all_nmon_file(path):
    if os.path.isfile(path):
        extend = path.rsplit(".", 1)
        if(len(extend) == 2):
            if extend[1] == "nmon":
                file_list.append(path)

    elif os.path.isdir(path):
        for file in os.listdir(path):
            get_all_nmon_file(path+"\\"+file)


def analyse_file(config):
    MircoFilePath = config.nmon_analyse_file
    get_all_nmon_file(config.nmon_file_dir)
    nmon_tuple = file_list
    path = config.nmon_result_file
    result = ExcelMicro.get_nmon_result_file(MircoFilePath, nmon_tuple, path)
    nr = NmonResult.NmonResult(result)
    nr.get_file(path=path)


def download_file(config):
    hostname = config.ip
    remotePath = config.remote_dir
    localPath = config.local_dir
    uesrname = config.username
    password = config.password
    ssh = SSHSokcet.sshSocket(hostname=hostname, username=uesrname, password=password)
    files = ssh.get_all_file(remotePath, remotePath, [])
    ssh.download_file(files, localPath, remotePath)


try:
    file_list = []
    config = RConfig.Config()
    config.reload_all_value()
    download_flag = config.download_flag

    if download_flag == 'True':
        download_file(config=config)
    elif download_flag != 'False':
        print("无法识别的下载标识")
        sys.exit()

    analyse_file(config=config)
except SystemExit:
    basepath = os.getcwd()
    file = open(basepath + "\\error.log", "w+", encoding='UTF-8')
    file.write("无法识别的下载标识, 配置文件中 download_flag 值只能为 True 或者 False")
    file.close()
except:
    basepath = os.getcwd()
    file = open(basepath + "\\error.log", "w+", encoding='UTF-8')
    file.write(traceback.format_exc())
    file.close()
