# -*- coding:utf-8 -*-
# @Time    : 2019/9/11 15:19
# @Author  : zengln
# @File    : report.py

import matplotlib.pyplot as plt

from performance_autotest.resultdata import *
from performance_autotest.log import logger
from performance_autotest.customexception import CustomError


class Report(object):

    # CPU 图片名称
    CPU_PIC_NAME = "CPU.png"
    # MEM 图片名称
    MEM_PIC_NAME = "MEM.png"
    # DISK 图片名称
    DISK_PIC_NAME = "DISK.png"
    # CPU 折线图的Title
    CPU_PIC_TITLE = "CPU 总负载"
    # MEM 折线图Title
    MEM_PIC_TITLE = "MEM 负载"
    # DISK 图片Title
    DISK_PIC_TITLE = "DISK 负载"
    # CPU 图 Y 轴标签
    CPU_PIC_Y_LABEL = "user% + sys%"
    # MEM 图 Y 轴标签
    MEM_PIC_Y_LABEL = "mem use and mem free (%)"
    # DISK 图左 Y 轴标签
    DISK_PIC_LY_LABEL = "disk write/read (kb/s)"
    # DISK 图右 Y 轴标签
    DISK_PIC_RY_LABEL = "disk io (IO/s)"
    # CPU 图 X 轴标签
    CPU_PIC_X_LABEL = "时间(HH:mm:ss)"
    # MEM 图 X 轴标签
    MEM_PIC_X_LABEL = "时间(HH:mm:ss)"
    # DISK 图 X 轴标签
    DISK_PIC_X_LABEL = "时间(HH:mm:ss)"
    # 刻度
    PIC_TICK = 15

    MEM_TOTAL = "MEM USE 实际使用内存(%)"
    MEM_FREE = "MEM FREE 空闲内存(%)"
    DISK_WRITE = "DISK WRITE (kb/s)"
    DISK_READ = "DISK READ (kb/s)"
    DISK_IO = "DISK IO (IO/s)"

    def get_report(self, result_list, nmon_list, file_name, file_path=""):
        """
        :param result_list: 压测结果 list
        :param nmon_list : nmon 结果 List
        :param file_name: html 报告名称
        :param file_path html 报告路径, 不填默认当前路径
        生成报告
        """
        logger.info("开始生成报告")
        load_result = self._change_to_load_table(result_list)
        nmon_result = self._change_to_nmon_table(nmon_list)
        file = file_path + os.path.sep + file_name
        with open(file, "w") as report_file:
            report_file.write(load_result)
            report_file.write(nmon_result)

        logger.info("生成报告结束")

    def _change_to_load_table(self, result_list):
        """
        将压测结果转化成 html 中的 table 返回
        :param result_list:需要转化的压测list
        :return: str table str
        """
        logger.info("开始将压测报告数据转化成 table")
        html_str = """
        <h1>summary</h1>
        <table border="1">
         <tr>
            <th>script name</th>
            <th>trasaction name</th>
            <th>trasaction number</th>
            <th>tps</th>
            <th>error%</th>
            <th>response time(average) ms</th>
            <th>response time(min) ms</th>
            <th>response time(max) ms</th>
        </tr>
        """
        for result in result_list:
            keys_dict = result.result_dict.keys()
            keys = list(keys_dict)
            if len(keys) == 0:
                raise CustomError("%s 脚本提取数据异常,无法获取到取样器" % result.name)

            logger.debug('%s 含有 transaction %s' % (result.name, keys))
            result_value_one = result.result_dict[keys[0]]
            summary_html_one = """
                  <tr>
                    <td rowspan= '%d'>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s%%</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                </tr>
                """ % (len(keys), result.name, keys[0], result_value_one[0], result_value_one[1], result_value_one[2],
                       result_value_one[3], result_value_one[4], result_value_one[5])

            if len(keys) == 1:
                html_str += summary_html_one
                continue

            for key_index in range(1, len(keys)):
                result_value = result.result_dict[keys[key_index]]
                summary_html = """
                <tr>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s%%</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>              
                </tr>
                """ % (
                    keys[key_index], result_value[0], result_value[1], result_value[2], result_value[3], result_value[4],
                    result_value[5])
                summary_html_one += summary_html

            html_str += summary_html_one

        return html_str + "</table>"


    def _change_to_nmon_table(self, nmon_list):
        """
        将nmon 结果转化成 html 中的 table 返回
        :param nmon_list:
        :return: str table str
        """
        logger.info("开始将nmon结果转化为 table")
        nmon_table_dict = {}
        for nmon in nmon_list:
            if nmon.ip in nmon_table_dict.keys():
                nmon_table_dict[nmon.ip].append(nmon)
            else:
                nmon_table_dict[nmon.ip] = []
                nmon_table_dict[nmon.ip].append(nmon)

        html_str = """
        <h1>Server resource(nmon)</h1>
        <table border="1">
         <tr>
            <th>server ip</th>
            <th>trasaction name</th>
            <th>cpu</th>
            <th>mem</th>
            <th>mem(contain virtual)</th>
            <th>diskread (kb/s)</th>
            <th>diskwrite (kb/s)</th>
            <th>diskio</th>
            <th>diskbusy</th>
            <th>netread (kb/s)</th>
            <th>netwrite (kb/s)</th>
        </tr>
        """
        for key in nmon_table_dict:
            nmon_table_value_one = nmon_table_dict[key][0]
            summary_html_one = """
                  <tr>
                    <td rowspan= '%d'>%s</td>
                    <td>%s</td>
                    <td>%s%%</td>
                    <td>%s%%</td>
                    <td>%s%%</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s</td>
                    <td>%s%%</td>
                    <td>%s</td>
                    <td>%s</td>
                </tr>
                """ % (len(nmon_table_dict[key]), key, nmon_table_value_one.name, nmon_table_value_one.cpu,
                       nmon_table_value_one.mem[0], nmon_table_value_one.mem[1], nmon_table_value_one.disk[0],
                       nmon_table_value_one.disk[1], nmon_table_value_one.disk[2], nmon_table_value_one.disk[3],
                       nmon_table_value_one.net[0], nmon_table_value_one.net[1])

            if len(nmon_table_dict[key]) == 1:
                html_str += summary_html_one
                continue

            for index in range(1, len(nmon_table_dict[key])):
                nmon_table_value = nmon_table_dict[key][index]
                summary_html = """
                      <tr>
                        <td>%s</td>
                        <td>%s%%</td>
                        <td>%s%%</td>
                        <td>%s%%</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s</td>
                        <td>%s%%</td>
                        <td>%s</td>
                        <td>%s</td>
                    </tr>
                    """ % (
                nmon_table_value.name, nmon_table_value.cpu, nmon_table_value.mem[0], nmon_table_value.mem[1],
                nmon_table_value.disk[0], nmon_table_value.disk[1], nmon_table_value.disk[2], nmon_table_value.disk[3],
                nmon_table_value.net[0], nmon_table_value.net[1])
                summary_html_one += summary_html

            html_str += summary_html_one
        return html_str + "</table>"

    def _create_cpu_char(self, x, y, path):
        '''
        根据监控数据数据, 生成 CPU 负载图
        :param x: x轴数据
        :param y: y轴数据,总cpu负载数据
        :param path: 图片保存路径
        :return: 是否成功生成图片
        '''
        if len(x) == 0 or len(y) == 0:
            return False

        # x,y 数据量不一致时会报错, 先判断一下x,y长度是否一致
        # 不一致则将较长的数据截取
        if len(x) > len(y):
            x = x[0:len(y)]
        elif len(x) < len(y):
            y = y[0:len(x)]

        # 设置 X 轴刻度, 数据太多 X 轴会显示太密, 抽取 X 轴部分数据作为刻度
        if len(x) > report.PIC_TICK:
            temp_x = []
            interval = len(x) // report.PIC_TICK
            for index in range(0, len(x), interval):
                temp_x.append(x[index])
            temp_x[-1] = x[-1]
            tick_x = temp_x
        else:
            tick_x = x

        tick_y = [x for x in range(0, 101, 5)]

        # 设置图片大小
        plt.figure(figsize=(16, 8))
        # 设置字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.plot(x, y)
        plt.xticks(tick_x)
        plt.yticks(tick_y)
        plt.xlabel(Report.CPU_PIC_X_LABEL)
        plt.ylabel(Report.CPU_PIC_Y_LABEL)
        plt.title(Report.CPU_PIC_TITLE)
        plt.savefig(path + os.path.sep + Report.CPU_PIC_NAME)
        return True

    def _create_mem_char(self, x, y, path):
        '''
        生成nmon 内存图
        :param x: x 轴数据
        :param y: y 轴数据,包括总内存与空闲内存数据[mem_total,mem_free]
        :param path: 图片保存路径
        :return: 图片是否生成成功
        '''
        # 没有获取到数据则直接返回失败
        if len(y[0]) == 0 or len(y[1]) == 0 or len(x) == 0:
            return False

        if len(x) != len(y[0]):
            if len(x) > len(y[0]):
                x = x[:len(y[0])]
            else:
                y[0] = y[0][:len(x)]

        if len(x) != len(y[1]):
            if len(x) > len(y[1]):
                x = x[:len(y[1])]
            else:
                y[1] = y[1][:len(x)]

        # 设置 X 轴刻度, 数据太多 X 轴会显示太密, 抽取 X 轴部分数据作为刻度
        if len(x) > report.PIC_TICK:
            temp_x = []
            interval = len(x) // report.PIC_TICK
            for index in range(0, len(x), interval):
                temp_x.append(x[index])
            temp_x[-1] = x[-1]
            tick_x = temp_x
        else:
            tick_x = x

        tick_y = [x for x in range(0, 101, 5)]

        # 设置图片大小
        plt.figure(figsize=(16, 8))
        # 设置字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.plot(x, y[0], label=Report.MEM_TOTAL)
        plt.plot(x, y[1], label=Report.MEM_FREE)
        plt.xticks(tick_x)
        plt.yticks(tick_y)
        plt.xlabel(Report.MEM_PIC_X_LABEL)
        plt.ylabel(Report.MEM_PIC_Y_LABEL)
        plt.title(Report.MEM_PIC_TITLE)
        # 图例位置自适应
        plt.legend(loc='best')
        plt.savefig(path + os.path.sep + Report.MEM_PIC_NAME)
        return True

    def _create_disk_char(self, x, y, path):
        '''
        生成nmon 磁盘图
        :param x: x 轴数据
        :param y: y 轴数据,包括disk write、disk read、disk io
        :param path: 图片保存路径
        :return: 图片是否生成成功
        '''
        # 没有获取到数据则直接返回失败
        if len(y[0]) == 0 or len(y[1]) == 0 or len(y[2]) == 0 or len(x) == 0:
            return False

        if len(x) != len(y[0]):
            if len(x) > len(y[0]):
                x = x[:len(y[0])]
            else:
                y[0] = y[0][:len(x)]

        if len(x) != len(y[1]):
            if len(x) > len(y[1]):
                x = x[:len(y[1])]
            else:
                y[1] = y[1][:len(x)]

        if len(x) != len(y[2]):
            if len(x) > len(y[2]):
                x = x[:len(y[2])]
            else:
                y[2] = y[2][:len(x)]

        # 设置 X 轴刻度, 数据太多 X 轴会显示太密, 抽取 X 轴部分数据作为刻度
        if len(x) > report.PIC_TICK:
            temp_x = []
            interval = len(x) // report.PIC_TICK
            for index in range(0, len(x), interval):
                temp_x.append(x[index])
            temp_x[-1] = x[-1]
            tick_x = temp_x
        else:
            tick_x = x

        # 设置图片大小
        fig, ax1 = plt.subplots(figsize=(16, 8))
        # 设置字体
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.title(Report.DISK_PIC_TITLE)

        ax1.plot(x, y[0], label=Report.DISK_WRITE)
        ax1.plot(x, y[1], label=Report.DISK_READ)
        ax1.set_xticks(tick_x)
        ax1.set_xlabel(Report.MEM_PIC_X_LABEL)
        ax1.set_ylabel(Report.DISK_PIC_LY_LABEL)

        # 第二个 Y 轴
        # ax2 = plt.twinx()
        # ax2.plot(x, y[2], label=Report.DISK_IO)
        # ax2.set_ylabel(Report.DISK_PIC_RY_LABEL)
        # ax2.set_xticks(tick_x)
        # 图例位置自适应
        # ax2.legend(loc='upper left')
        ax1.legend(loc='upper right')
        plt.savefig(path + os.path.sep + Report.DISK_PIC_NAME)
        return True

if __name__ == '__main__':
    nmon_list = []
    # nmon_file = [r'D:\work\工具\nmon\71Vusr.nmon', r'D:\work\工具\nmon\znzfdb1_190703_1936.nmon']
    nmon_file = [r'D:\pycharm\workspace\ztools\performance_autotest\test\nmon\组合场景-50-12h-129.nmon']
    for index in range(0, len(nmon_file)):
        nmon = NmonAnalyse()
        nmon.ip = "127.0.0.1"
        nmon.file_analyse(nmon_file[index])
        nmon_list.append(nmon)

    # jmeter_list = []
    # jmeter_file = [r"C:\Users\zengjn\Desktop\jemter\get", r"C:\Users\zengjn\Desktop\jemter\get_1"]
    # for index in range(0, len(jmeter_file)):
    #     jmeter = JmeterAnalyse()
    #     jmeter.file_analyse(jmeter_file[index])
    #     jmeter_list.append(jmeter)
    #
    # loadrunner_list = []
    # loadrunner_file = [r'C:\Users\zengjn\Desktop\Get\scenario\Scenario-5', r'C:\Users\zengjn\Desktop\Get\scenario\res', r'C:\Users\zengjn\Desktop\get1\res\res']
    # for index in range(0, len(loadrunner_file)):
    #     loadrunner = LoadRunnerAnalyse()
    #     loadrunner.file_analyse(loadrunner_file[index])
    #     loadrunner_list.append(loadrunner)
    #
    report = Report()
    report._create_cpu_char(nmon_list[0].time, nmon_list[0].cpus, ".")
    report._create_mem_char(nmon_list[0].time, nmon_list[0].mems, ".")
    report._create_disk_char(nmon_list[0].time, nmon_list[0].disks, ".")

    # report.get_report(loadrunner_list, nmon_list)

