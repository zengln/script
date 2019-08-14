# -*- coding:utf-8 -*-

# @Time    : 2019/8/13 23:40
# @Author  : zengln
# @Filename: test.py

import os
import xlrd
from xlutils.copy import copy

excle_path = r'D:\MyDocument\nmon\新建文件夹\excel文件夹'
txt_path = r'D:\MyDocument\nmon\新建文件夹\txt文件'


def get_all_file(path):
    """
    获取当前路径下所有文件
    :param path: 路径
    :return: 包含传入路径下所有文件绝对路径的列表，返回的列表结构是[传入路径,[路径下所有文件]]
    """
    file_list = [path]
    for root, subdir, file in os.walk(path):
        file_list.append(file)

    return file_list


def txt_match_excel(txt_list, excel_list):
    """
    将 txt 文件与 excel 文件对应,返回有对应关系的列表
    :param txt_list: txt 文件名列表
    :param excel_list: excel 文件名列表
    :return: 返回一个元组(匹配关系列表, 未匹配文件列表)
    """
    match_list = []
    un_match_list = []
    txt_list_unmatch = txt_list.copy()
    excel_list_unmatch = []
    for excel_file in excel_list:
        excel_name = excel_file.split("_")[0]
        excel_match_txt = [excel_file]
        for txt_file in txt_list:
            if excel_name in txt_file:
                excel_match_txt.append(txt_file)
                txt_list_unmatch.remove(txt_file)
        if excel_match_txt.__len__() != 0:
            match_list.append(excel_match_txt)
        else:
            excel_list_unmatch.append(excel_file)

    un_match_list.append(excel_list_unmatch)
    un_match_list.append(txt_list_unmatch)
    return match_list, un_match_list


def print_unmatch_file(unmatch_list):
    """
    打印出未匹配到的文件
    :param unmatch_list: 未匹配文件列表
    """
    excel_files = un_match_list[0]
    txt_files = un_match_list[1]
    if excel_files.__len__() != 0:
        print("未匹配到对应 txt 的 excel 文件:")
        for excel_file in excel_files:
            print(excel_file)

    if txt_files.__len__() != 0:
        print("未匹配到对应 excel 的 txt 文件:")
        for txt_file in txt_files:
            print(txt_file)


def write_to_excel(match_list):
    """
    将匹配到的 txt 文件内容写入对应 excel
    :param match_list: 匹配到的文件列表
    :return: None
    """
    for match_file in match_list:
        if len(match_file) < 2:
            continue

        old_excel = xlrd.open_workbook(excle_path + "\\" + match_file[0])
        new_excel = copy(old_excel)
        ws = new_excel.get_sheet(0)
        sheet = old_excel.sheet_by_index(0)
        row_num = sheet.nrows
        col_num = sheet.ncols
        for row_index in range(0, row_num):
            if "yq_respcode_xz" in sheet.cell_value(row_index, 0):
                yq_index = row_index
                break
            elif row_index == row_num - 1:
                # 新增行
                ws.write(row_num, 0, "yq_respcode_xz")
                ws.write(row_num + 1, 0, "yq_respmsg_xz")
                ws.write(row_num + 2, 0, "yq_serviceStatus_xz")
                # 修改行
                ws.write(row_num + 3, 0, "yq_respcode_xg")
                ws.write(row_num + 4, 0, "yq_respmsg_xg")
                ws.write(row_num + 5, 0, "yq_serviceStatus_xg")
                # 删除行
                ws.write(row_num + 6, 0, "yq_respcode_sc")
                ws.write(row_num + 7, 0, "yq_respmsg_sc")
                ws.write(row_num + 8, 0, "yq_serviceStatus_sc")

        txt_files = match_file[1:]
        for txt_file in txt_files:
            file = open(txt_path + "\\" + txt_file, mode='r')
            if "新增" in txt_file:
                row_index_yq = yq_index
            elif "修改" in txt_file:
                row_index_yq = yq_index + 3
            elif "删除" in txt_file:
                row_index_yq = yq_index + 6
            else:
                print("未识别的结果文档: "+ txt_file)
                file.close()
                continue

            for line in file:
                results = line.strip("\n").split(",")
                casename = results[0]
                for col_index in range(1, col_num):
                    excel_casename = str(sheet.cell_value(0, col_index))
                    if excel_casename.strip() == casename.strip():
                        ws.write(row_index_yq, col_index, results[1])
                        ws.write(row_index_yq + 1, col_index, results[2])
                        ws.write(row_index_yq + 2, col_index, results[3])

            file.close()

        new_excel.save(excle_path + "\\" + match_file[0])


excel_files = get_all_file(excle_path)
txt_files = get_all_file(txt_path)
match_list, un_match_list = txt_match_excel(txt_list=txt_files[1], excel_list=excel_files[1])
print_unmatch_file(un_match_list)
write_to_excel(match_list)
