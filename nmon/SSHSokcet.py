# -*- coding:utf-8 -*-

# create: 2019-07-29
# author:zengln
# desc: SSH 连接远程服务器下载指定文件夹或文件

import paramiko
import os
from stat import S_ISDIR
from nmon.NmonLog import log


class sshSocket(object):

    def __init__(self, hostname, username, password):
        tran = paramiko.Transport((hostname, 22))
        tran.connect(username=username, password=password)
        self.sftp = paramiko.SFTPClient.from_transport(tran)

    def get_all_file(self, path, basepath, filelist):
        files = self.sftp.listdir_attr(path)

        if basepath == path:
            last_index = basepath.rfind("/")
            root = basepath[last_index+1:]
            basepath = basepath[:last_index]
            if root == "":
                last_index = basepath[:last_index].rfind("/")
                root = basepath[last_index+1:]
                basepath = basepath[:last_index]
        else:
             root = path[basepath.__len__() + 1:]


        for file in files:
            if S_ISDIR(file.st_mode):
                newpath = path + "/" + file.filename
                self.get_all_file(newpath, basepath, filelist)
            else:
                if root == "":
                    filelist.append(file.filename)
                else:
                    filelist.append(root + "/" + file.filename)

        return filelist


    def download_file(self,filespath, localpath, remotepath):
        if not os.path.exists(localpath):
            os.makedirs(localpath)

        for filepath in filespath:
            winfilepath = localpath + "\\" + filepath.replace("/", "\\")
            winpathindex = winfilepath.rfind("\\")
            winpath = winfilepath[:winpathindex]
            root_index = filepath.find("/")
            log.info("正在下载:" + winfilepath[winpathindex+1:])
            if not os.path.exists(winpath):
                os.makedirs(winpath)

            file = open(winfilepath, 'w')
            file.close()
            self.sftp.get(remotepath + "/" + filepath[root_index:], winfilepath)

