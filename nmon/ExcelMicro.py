# -*- coding:utf-8 -*-

# create:2018-05-23
# author:zengln
# desc：excel micro 操作类

import win32com.client
import pythoncom
import win32api
import os

'''
    @:param
    micro_file：宏文件(全路径)
    nmon_files：待解析的 nmon 文件
    save_path ：解析文件的储存路径(仅在待解析的 nmon 文件数量为一的时候生效), 不传默认与 nmon 文件同路径
    @:return
    返回解析文件路径
'''


def get_nmon_result_file(micro_file, nmon_files, save_path = ""):
    x1 = win32com.client.Dispatch("Excel.Application")
    x1.Visible = True
    nmon_tuple = [0]
    result_file = []

    for index in range(0, len(nmon_files)):
        check_file(nmon_files[index], nmon_tuple)

    x1.Workbooks.Open(micro_file)

    if save_path != "" and len(nmon_files) == 1:
        result_file.append(save_path)
    elif save_path == "" and len(nmon_files) == 1:
        save_path = nmon_files[0] + ".xlsx"
        result_file.append(save_path)
    else:
        for i in range(0, len(nmon_files)):
            result_file.append(nmon_files[i] + ".xlsx")

    try:
        x1.Application.Run("Main", 0, save_path, nmon_tuple)
    except pythoncom.com_error as error:
        print(win32api.FormatMessage(error.excepinfo[0]))

    x1.Quit()
    return result_file


'''
    检查给定的数组是否内容为文件
    若为文件夹则将文件夹内的所有文件都添加到数组内
'''


def check_file(nmon_files, file_tuple):
    if os.path.isfile(nmon_files):
        file_tuple.append(nmon_files)
    else:
        file_list = os.listdir(nmon_files)
        for index in range(0, len(file_list)):
            file_name = os.path.join(nmon_files, file_list[index])
            check_file(file_name, file_tuple)




