# -*- coding:utf-8 -*-

# create: 2018-05-22
# author:zengln
# desc: Nmon 解析结果文件取值

import xlrd
import xlwt
import re

from xlutils.copy import copy

class NmonResult(object):

    '''
        创建 NmonResult 对象时, 需要传入解析出的结果文件全路径地址
        参数仅支持字符串或数组
    '''
    def __init__(self, nmonfiles):
        if not isinstance(nmonfiles, (str, tuple, list)):
            print(type(nmonfiles))
            raise TypeError("参数类型错误, 仅支持字符串、数组与列表")

        self.__nFiles = []
        if isinstance(nmonfiles, str) and nmonfiles.strip() != "":
            self.__nFiles.append(nmonfiles)
        elif isinstance(nmonfiles, (tuple, list)) and nmonfiles.__len__() != 0:
            self.__nFiles = nmonfiles
        else:
            raise RuntimeError("传入的解析文件不能为空, 必须为字符串或者字符串数组")

        self.__workbook = xlrd.open_workbook(self.__nFiles[0])


    '''
        提供简单的提取数据需求
    '''
    def get_file(self, path=r'D:\test.xls'):
        file_num = self.__nFiles.__len__()
        wbk = xlwt.Workbook()
        sheet = wbk.add_sheet('sheet1')
        sheet.write(0, 0, "文件路径")
        sheet.write(0, 1, "CPU")
        sheet.write(0, 2, "MEMORY")
        sheet.write(0, 3, "NETWORK")
        sheet.write(0, 4, "DISKI/O")
        for index in range(0, file_num):
            workbook = xlrd.open_workbook(self.__nFiles[index])
            # 读取内容
            cpu = self.get_avg_cpu(workbook)
            mem = self.get_avg_mem(workbook)
            net = self.get_avg_net(workbook)
            disk = self.get_avg_disk_write(workbook)
            # 写入新的 excel 中
            sheet.write(index + 1, 0, self.__nFiles[index])
            sheet.write(index + 1, 1, cpu[2])
            sheet.write(index + 1, 2, mem)
            sheet.write(index + 1, 3, net[2])
            sheet.write(index + 1, 4, disk)
        wbk.save(path)


    '''
        分页保存提取结果
        sheet 名以数组形式传入
        将地址中含有对应 sheet 页名称的数据提取到对应页面
        否则默认保存到sheet1
    '''
    def get_multi_page_file(self, sheet_names):
        file_num = self.__nFiles.__len__()
        file_row_dict = {'sheet1': 0}
        wbk = xlwt.Workbook()
        wbk.add_sheet('sheet1')
        for sheet_index in range(0, len(sheet_names)):
            wbk.add_sheet(sheet_names[sheet_index])
            file_row_dict[sheet_names[sheet_index]] = 0

        for file_index in range(0, file_num):
            workbook = xlrd.open_workbook(self.__nFiles[file_index])
            # 读取内容
            cpu = self.get_avg_cpu(workbook)
            mem = self.get_avg_mem(workbook)
            net = self.get_avg_net(workbook)
            disk = self.get_avg_disk_write(workbook)
            sheet = wbk.get_sheet(wbk.sheet_index('sheet1'))

            current_sheet = "sheet1"

            #找到对应的sheet页面,并写入
            for sheet_name_index in range(0, len(sheet_names)):
                pattern_str = sheet_names[sheet_name_index]
                pattern = re.compile(pattern_str, re.S)
                result = re.search(pattern, self.__nFiles[file_index])
                if result != None:
                    sheet = wbk.get_sheet(wbk.sheet_index(sheet_names[sheet_name_index]))
                    current_sheet = sheet_names[sheet_name_index]
                    break

            row_index = file_row_dict[current_sheet]
            file_row_dict[current_sheet] = row_index + 1
            sheet.write(row_index, 0, self.__nFiles[file_index])
            sheet.write(row_index, 1, cpu[2])
            sheet.write(row_index, 2, mem)
            sheet.write(row_index, 3, net[2])
            sheet.write(row_index, 4, disk)

        wbk.save(r'C:\test.xls')


    '''
        返回第一个文件的 workbook
    '''
    def get_work_book(self):
        return self.__workbook

    '''
        写指定 excel 文件
        @param:
        file_path: 文件全路径
        sheet_name: sheet 名
        row：行
        col:列
        data:数据
        
    '''
    def write_excel(self, file_path, sheet_name, row, col, data):
        rd = xlrd.open_workbook(file_path)
        wb = copy(rd)
        ws = wb.get_sheet(wb.sheet_index(sheet_name))
        ws.write(row, col, data)
        wb.save(file_path)

    '''
        返回一个数组, 内容如下:
        [User,Sys,Cpu]
    '''
    def get_avg_cpu(self, workbook):
        sheet = workbook.sheet_by_name("CPU_ALL")
        results = []
        results.append(sheet.cell_value(sheet.nrows-1, 1))
        results.append(sheet.cell_value(sheet.nrows-1, 2))
        results.append(sheet.cell_value(sheet.nrows-1, sheet.ncols-1))
        return results

    '''
        MEM
        Linux内存平均计算公式:
        (Memtotal - Memfree - cached - buffers)/Memtotal  * 100
        即( =(B2-F2-K2-N2)/B2*100)
        AIX内存平均计算公式:
        (Real total + Virtuak total - Real Free - Virtual Free)/(Real total + Virtual total) * 100
        即(=(F2+G2-D2-E2)/(F2+G2))*100
    '''
    def get_avg_mem(self, workbook):
        sheet = workbook.sheet_by_name("MEM")
        avg_sum = 0
        if sheet.ncols == 16:
            for index in range(1, sheet.nrows):
                b = sheet.cell_value(index, 1)
                f = sheet.cell_value(index, 5)
                k = sheet.cell_value(index, 10)
                n = sheet.cell_value(index, 13)
                avg = (b-f-k-n)/b*100
                avg_sum = avg_sum + avg
        elif sheet.ncols == 7:
            for index in range(1, sheet.nrows):
                d = sheet.cell_value(index, 3)
                e = sheet.cell_value(index, 4)
                f = sheet.cell_value(index, 5)
                g = sheet.cell_value(index, 6)
                avg = (f+g-d-e)/(f+g)*100
                avg_sum = avg_sum + avg
        else:
            return "无法识别的内存页"
        return avg_sum/(sheet.nrows-1)

    '''
        Net
        返回非 0 列的read、write、total平均值,放入数组中, 返回内容如下:
        [read, write, total]
    '''
    def get_avg_net(self, workbook):
        sheet = workbook.sheet_by_name("NET")
        results = []
        if int(sheet.cell_value(1, 1)) != 0:
            index_col = 1
        else:
            index_col = 2
        for i in range(0, 3):
            sum = 0
            for index_row in range(1, sheet.nrows-5):
                sum = sum + sheet.cell_value(index_row, index_col)
            results.append(sum/(sheet.nrows-5))
            index_col = index_col + 2
        return results

    '''
        DISKWRITE
        取 sdb 列平均值返回
    '''
    def get_avg_disk_write(self, workbook):
        sheet = workbook.sheet_by_name("DISKWRITE")
        return sheet.cell_value(sheet.nrows-4, 1)

    '''
        DISKREAD
        取 sda 列平均值返回
    '''
    def get_avg_disk_read(self, workbook):
        sheet = workbook.sheet_by_name("DISKREAD")
        return sheet.cell_value(sheet.nrows-4, 1)

    '''
        传入表名, 行数, 列数获取指定单元格内容
    '''
    def get_cell_value(self, workbook, sheet_name, row, col):
        sheet_names = workbook.sheet_names()
        if sheet_name not in sheet_names:
            raise RuntimeError("表不存在")

        if row > workbook.sheet_by_name(sheet_name).nrows:
            raise RuntimeError("超过最大行数")

        if col > workbook.sheet_by_name(sheet_name).ncols:
            raise RuntimeError("超过最大列数")

        return workbook.sheet_by_name(sheet_name).cell_value(row, col)