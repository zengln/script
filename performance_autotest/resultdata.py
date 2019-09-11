# -*- coding:utf-8 -*-
# @Time    : 2019/8/30 13:56
# @Author  : zengln
# @File    : resultdata.py

import json
import re
import os.path

from performance_autotest.log import logger
from performance_autotest.customexception import CustomError


class FileAnalyse(object):
    """
    文件解析基础接口
    """
    def __init__(self):
        self.name = None

    def file_analyse(self, file):
        self.name = os.path.basename(file)


class NmonAnalyse(FileAnalyse):

    def __init__(self):
        # 初始化变量
        super().__init__()
        self.cpu = float(0)
        self.mem = float(0)
        self.disk = float(0)
        self.net = float(0)

    def file_analyse(self, file):
        """
        Nmon 文件解析入口
        :param file nmon 文件全路径
        """
        logger.info("%s 文件数据解析开始" % os.path.basename(file))
        super().file_analyse(file)
        cpu_line = []
        mem_line = []
        disk_line = []
        net_line = []
        # 打开文件, 提取存有关键数据的行
        with open(file, "r") as nmonfile:
            text = nmonfile.readlines()
            for line in text:
                # cpu
                if "CPU_ALL,T" in line:
                    cpu_line.append(line)
                # mem
                elif "MEM,T" in line:
                    mem_line.append(line)
                # disk
                elif "DISK" in line:
                    disk_line.append(line)
                # net
                elif "NET," in line:
                    net_line.append(line)

        # 分别对关键数据进行处理
        logger.info("开始提取cpu数据")
        self.fetch_cpu(cpu_line)
        logger.info("开始提取内存数据")
        self.fetch_mem(mem_line)
        logger.info("开始提取磁盘数据")
        self.fetch_disk(disk_line)
        logger.info("开始提取网络数据")
        self.fetch_net(net_line)
        logger.info("%s 文件数据解析结束" % os.path.basename(file))

    def fetch_cpu(self, lines):
        """
        :param lines: 带 cpu 关键数据行
        """
        cpu_sum = float(0)
        for line in lines:
            cpus = line.split(",")
            # sys% datas[2] user datas[3]
            # total = sys + user
            cpu_sum += (float(cpus[3]) + float(cpus[2]))
        self.cpu = round(cpu_sum / len(lines), 2)
        logger.debug("cpu: %.2f%%" % self.cpu)

    def fetch_mem(self, lines):
        """
        获取 mem 的关键数据包括: 纯物理内存使用率, 包含虚拟内存的内存使用率(无则为0)
        :param lines: 带 mem 关键数据行
        """
        mem_sum = float(0)
        mem_virtual_sum = float(0)
        for line in lines:
            mems = line.split(",")
            if len(mems) == 17:
                # (Memtotal - Memfree - cached - buffers)/Memtotal  * 100
                mem_sum += ((float(mems[2]) - float(mems[6]) - float(mems[11]) - float(mems[14])) / float(
                    mems[2]) * 100)
            elif len(mems) == 8:
                # (Real total - Real free)/Real total * 100
                mem_sum += ((float(mems[6]) - float(mems[4])) / float(mems[6]) * 100)
                # (Real total - Real free + Virtual total - Virtual free) /(Real total + Virtual total) * 100
                mem_virtual_sum += ((float(mems[6]) - float(mems[4]) + float(mems[7]) - float(mems[5])) / (
                            float(mems[6]) + float(mems[7])) * 100)
            else:
                raise CustomError("暂不支持此内存页面数据读取")

        self.mem = (round(mem_sum / len(lines), 2), round(mem_virtual_sum / len(lines), 2))
        logger.debug("mem: 不含虚拟内存的使用率 %.2f%%, 包含虚拟内存的使用率 %.2f%%" % (self.mem[0], self.mem[1]))

    def fetch_disk(self, lines):
        """
        获取 disk 的关键数据包括: disk-read(KB/S),disk-write(KB/S),io(io/s),disk-busy(%)
        :param lines: 带 disk 关键数据行
        """
        # 累加和
        diskread_sum = float(0)
        diskwrite_sum = float(0)
        diskio_sum = float(0)

        # diskbusy 每列均值
        diskbusy_avg = []

        # diskbusy 最大值
        diskbusy_max = float(0)

        # 次数统计
        diskread_num = 0
        diskwrite_num = 0
        diskio_num = 0
        diskbusy_num = 0
        for line in lines:
            disks = line.split(",")
            if "DISKREAD,T" in line:
                # diskread
                disk_read_line_sum = float(0)
                # 统计每行之和
                for diskread_index in range(2, len(disks)):
                    disk_read_line_sum += float(disks[diskread_index])
                # 累加
                diskread_sum += disk_read_line_sum
                # 计算总行数
                diskread_num += 1
            elif "DISKWRITE,T" in line:
                # diskwrite
                disk_write_line_sum = float(0)
                # 统计每行之和
                for diskwrite_index in range(2, len(disks)):
                    disk_write_line_sum += float(disks[diskwrite_index])
                # 累加
                diskwrite_sum += disk_write_line_sum
                # 计算总行数
                diskwrite_num += 1
            elif "DISKXFER,T" in line:
                # 每秒 IO 操作次数
                disk_io_line_sum = float(0)
                # 统计每行之和
                for diskio_index in range(2, len(disks)):
                    disk_io_line_sum += float(disks[diskio_index])
                # 累加
                diskio_sum += disk_io_line_sum
                # 计算总行数
                diskio_num += 1
            elif "DISKBUSY,T" in line:
                # 获取 busi 每列初始值
                if len(diskbusy_avg) == 0:
                    for disk_busy_line_index in range(2, len(disks)):
                        diskbusy_avg.append(float(disks[disk_busy_line_index]))
                else:
                    diskbusy_num += 1
                    # 计算 busi 每列均值
                    for disk_busy_line_index in range(2, len(disks)):
                        diskbusy_avg[disk_busy_line_index - 2] = (float(
                            diskbusy_avg[disk_busy_line_index - 2]) * diskbusy_num + float(
                            disks[disk_busy_line_index])) / (diskbusy_num + 1)

        # 获取 busi 最大列的均值
        for disk_busy in diskbusy_avg:
            if disk_busy > diskbusy_max:
                diskbusy_max = disk_busy

        self.disk = (round(diskread_sum / diskread_num, 2), round(diskwrite_sum / diskwrite_num, 2),
                     round(diskio_sum / diskio_num, 2), round(diskbusy_max, 2))
        logger.debug("disk: diskread %.2f, diskwrite %.2f, diskio %.2f, diskbusy %.2f%%" % (
            self.disk[0], self.disk[1], self.disk[2], self.disk[3]))

    def fetch_net(self, lines):
        """
        获取 net read(KB/s) 和 write(KB/s) 均值
        :param lines:包含 net 关键数据的行
        :return:
        """
        # read 列索引
        net_read_index = []
        # write 列索引
        net_write_index = []
        # 所有 raad 列均值
        net_read = []
        # 所有 write 列均值
        net_write = []
        # read 列均值最大值
        net_read_max = float(0)
        # write 列均值最大值
        net_write_max = float(0)

        for line in lines:
            disks = line.split(",")
            if not "NET,T" in line:
                for net_name_index in range(2, len(disks)):
                    net_name = disks[net_name_index]
                    # 获取 read 所在列
                    if "read" in net_name:
                        avg_read = 0
                        net_read_index.append(net_name_index)
                    # 获取 write 所在列
                    elif "write" in net_name:
                        avg_write = 0
                        net_write_index.append(net_name_index)
            else:
                # 获取每个 read 列的均值
                if not len(net_read_index) == 0:
                    avg_read += 1
                    net_read_len_index = 0
                    for net_read_num_index in net_read_index:
                        if avg_read == 1:
                            net_read.append(float(disks[net_read_num_index]))
                        else:
                            net_read[net_read_len_index] = (float(net_read[net_read_len_index]) * (avg_read - 1) + float(
                                disks[net_read_num_index])) / avg_read
                            net_read_len_index += 1
                # 获取每个 write 列的均值
                if not len(net_write_index) == 0:
                    avg_write += 1
                    net_write_len_index = 0
                    for net_write_num_index in net_write_index:
                        if avg_write == 1:
                            net_write.append(float(disks[net_write_num_index]))
                        else:
                            net_write[net_write_len_index] = (float(net_write[net_write_len_index]) * (
                                        avg_write - 1) + float(disks[net_write_num_index])) / avg_write
                            net_write_len_index += 1

        for net_read_avg in net_read:
            if net_read_avg > net_read_max:
                net_read_max = net_read_avg

        for net_write_avg in net_write:
            if net_write_avg > net_write_max:
                net_write_max = net_write_avg

        self.net = (round(net_read_max, 2), round(net_write_max, 2))
        logger.debug("net: 网络读取最大值 %.2f, 网络写入最大值 %.2f" % (self.net[0], self.net[1]))


class JmeterAnalyse(FileAnalyse):

    def __init__(self):
        # 保存解析结果
        super().__init__()
        self.result_dict = {}

    def file_analyse(self, file):
        """
        解析jmeter报告
        :param file: jmeter报告所在目录
        """
        logger.info("开始解析%s jmeter结果文件" % os.path.basename(file))
        super().file_analyse(file)
        file_all_path = file + r"\content\js\dashboard.js"

        with open(file_all_path, "r") as jmeterfile:
            text = jmeterfile.read()
            static_data_match_result = re.match(r'[\s\S]*statisticsTable"\),(.*?), function', text)

            if static_data_match_result is not None:
                static_json_data = static_data_match_result.group(1).strip()
                logger.debug("取到 %s 的压测结果数据为: %s" % (os.path.basename(file), static_json_data))
                static_data = json.loads(static_json_data)
                logger.debug("转化成json格式:%s" % static_data)

                if "items" not in static_data.keys():
                    raise CustomError("%s获取压测结果失败,提取到的数据中未找到item标签" % os.path.basename(file))

                static_items_data = static_data["items"]
                logger.debug("提取到的数据为: %s" % static_items_data)
                for static_item_data in static_items_data:
                    tmp_data = static_item_data['data']
                    # list: [Transaction, TPS, Error%, Response Time(average), Response Time(min), Response Time(max)]
                    tmp_list = [tmp_data[1], tmp_data[10], tmp_data[3], tmp_data[4], tmp_data[5], tmp_data[6]]
                    # dict: {name:list}
                    self.result_dict[tmp_data[0]] = tmp_list

                logger.debug("%s 提取结果 %s" % (os.path.basename(file), self.result_dict))

            else:
                raise CustomError("%s获取压测结果失败,未找到匹配数据" % os.path.basename(file))

        logger.info("jmeter 结果文件解析结束")


class LoadRunnerAnalyse(FileAnalyse):

    def __init__(self):
        super().__init__()
        self.result_dict = {}

    def file_analyse(self, file):
        """
        解析 Loadrunner 报告
        :param file: loadrunner 报告所在路径
        """
        logger.info("开始解析 %s loadrunner 报告" % os.path.basename(file))
        super().file_analyse(file)
        file_all_path = file + r'\An_Report1\summary.html'
        with open(file_all_path, "r") as loadrunnerfile:
            text = loadrunnerfile.read()
            tps_match = re.match(r'[\s\S]*headers="LraPer second".*?8">(.*?)</td>', text)
            logger.debug("tps_match is None: %s" % str(False if(tps_match is not None) else True))
            pass_match = re.match(r'[\s\S]*headers="LraPass".*?8">(.*?)</td>', text)
            logger.debug("pass_match is None: %s" % str(False if (pass_match is not None) else True))
            fail_match = re.match(r'[\s\S]*headers="LraFail".*?8">(.*?)</td>', text)
            logger.debug("fail_match is None: %s" % str(False if (fail_match is not None) else True))
            resp_avg_match = re.match(r'[\s\S]*headers="LraAverage".*?8">(.*?)</td>', text)
            logger.debug("resp_avg_match is None: %s" % str(False if (resp_avg_match is not None) else True))
            resp_min_match = re.match(r'[\s\S]*headers="LraMinimum".*?8">(.*?)</td>', text)
            logger.debug("resp_min_match is None: %s" % str(False if (resp_min_match is not None) else True))
            resp_max_match = re.match(r'[\s\S]*headers="LraMaximum".*?8">(.*?)</td>', text)
            logger.debug("resp_max_match is None: %s" % str(False if (resp_max_match is not None) else True))

            if tps_match is None or pass_match is None or fail_match is None or resp_avg_match is None or resp_min_match is None or resp_max_match is None:
                raise CustomError("%s 有未匹配到的数据" % os.path.basename(file))

            # 长整数取到的数字带有逗号,例如1024是1,024,在取数字时,先将逗号去掉
            tps = tps_match.group(1).replace(",", "")
            logger.debug("tps: %s" % tps)
            pass_tsc = pass_match.group(1).replace(",", "")
            logger.debug("pass transaction: %s" % pass_tsc)
            fail_tsc = fail_match.group(1).replace(",", "")
            logger.debug("fail transaction: %s" % fail_tsc)
            # 时间转化成 ms 单位
            resp_avg = float(resp_avg_match.group(1).replace(",", "")) * 1000
            logger.debug("resp average time : %sms" % resp_avg)
            resp_max = float(resp_max_match.group(1).replace(",", "")) * 1000
            logger.debug("resp max time: %sms" % resp_max)
            resp_min = float(resp_min_match.group(1).replace("", "")) * 1000
            logger.debug("resp min time: %sms" % resp_min)

            all_tsc = str(int(fail_tsc) + int(pass_tsc))
            error = round(int(fail_tsc)/int(all_tsc), 2)
            # list: [Transaction, TPS, Error%, Response Time(average), Response Time(min), Response Time(max)]
            data_list = [all_tsc, tps, error, resp_avg, resp_min, resp_max]
            self.result_dict[os.path.basename(file)] = data_list
            logger.info("loadrunner 报告解析结束")

if __name__ == "__main__":
    # nmonfile = r'D:\work\工具\nmon\71Vusr.nmon'
    # nmonfile = r'D:\work\工具\nmon\znzfdb1_190703_1936.nmon'
    # nmon = NmonAnalyse()
    # nmon.file_analyse(nmonfile)
    # print(nmon.cpu)
    # print(nmon.mem)
    # print(nmon.disk)
    # print(nmon.net)
    # jmetrfile = r"C:\Users\zengjn\Desktop\jemter\get"
    # jmeter = JmeterAnalyse()
    # jmeter.file_analyse(jmetrfile)
    loadrunner_file = r'C:\Users\zengjn\Desktop\Get\scenario\res-5'
    loadrunner = LoadRunnerAnalyse()
    loadrunner.file_analyse(loadrunner_file)