# -*- coding:utf-8 -*-

from nmon import ExcelMicro
from nmon import NmonResult
from nmon import RConfig
import traceback
import os


def get_all_nmon_file(path):
    if os.path.isfile(path):
        extend = path.rsplit(".", 1)
        if(len(extend) == 2):
            if extend[1] == "nmon":
                file_list.append(path)

    elif os.path.isdir(path):
        for file in os.listdir(path):
            get_all_nmon_file(path+"\\"+file)


try:
    file_list = []
    config = RConfig.Config()
    config.reload_all_value()
    basepath = os.getcwd()
    MircoFilePath = config.nmon_analyse_file
    get_all_nmon_file(config.nmon_file_dir)
    nmon_tuple =file_list
    path = config.nmon_result_file
    result = ExcelMicro.get_nmon_result_file(MircoFilePath, nmon_tuple, path)
    nr = NmonResult.NmonResult(result)
    nr.get_file(path=path)
except:
    file = open(basepath + "\\error.log", "w+")
    file.write(traceback.format_exc())
    file.close()
