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
        # 初始化ip
        self.ip = "未设置IP地址"
        # cpu平均负载
        self.cpu = float(0)
        # 内存平均负载
        self.mem = float(0)
        # 磁盘负载
        self.disk = float(0)
        # 网络负载
        self.net = float(0)
        # cpu 负载数据, [cpu_total]
        self.cpus = []
        # 内存负载数 [mem_use,mem_free]
        self.mems = []
        # 网络负载数据
        self.nets = []
        # 磁盘负载数据 [disk_write,disk_read,disk_io]
        self.disks = []
        # 监控时间,生成报告图表中的X轴使用数据
        self.time = []

    def set_ip(self, ip):
        self.ip = ip

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
        time_line = []
        # 打开文件, 提取存有关键数据的行
        with open(file, "r", encoding='utf8') as nmonfile:
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
                # time
                elif "ZZZZ,T" in line:
                    # NMON 文件中存在监控数据未与其他行分隔开
                    # 判断当前数据行是否以 "ZZZZ,T" 开头, 如果不是则分割
                    index = line.find("ZZZZ,T")
                    if index != 0:
                        line = line[index:-1]

                    time_line.append(line)

        # 分别对关键数据进行处理
        logger.info("开始提取cpu数据")
        self.fetch_cpu(cpu_line)
        logger.info("开始提取内存数据")
        self.fetch_mem(mem_line)
        logger.info("开始提取磁盘数据")
        self.fetch_disk(disk_line)
        logger.info("开始提取网络数据")
        self.fetch_net(net_line)

        # 获取时间, 用于后续生成图像数据的X轴
        self.fetch_time(time_line)
        logger.info("%s 文件数据解析结束" % os.path.basename(file))

    def fetch_time(self, lines):
        '''
        提取监控采集点的时间
        :param lines:
        :return: None
        '''
        for line in lines:
            times = line.split(",")
            self.time.append(times[2])

    def fetch_cpu(self, lines):
        """
        :param lines: 带 cpu 关键数据行
        """
        # 解析数据错误行数
        error_num = 0
        # cpu总负载
        cpu_sum = float(0)
        # cpu负载数据
        cpu_num_list = []
        for line in lines:
            # NMON 文件中存在监控数据未与其他行分隔开
            # 判断当前数据行是否以 "CPU_ALL,T" 开头, 如果不是则分割
            index = line.find("CPU_ALL,T")
            if index != 0:
                line = line[index:-1]

            # cpu 数据计算
            cpus = line.split(",")
            # sys% datas[2] user datas[3]
            # total = sys + user
            try:
                line_cpu_sum = float(cpus[3]) + float(cpus[2])
                cpu_sum += line_cpu_sum
                cpu_num_list.append(line_cpu_sum)
            except Exception:
                logger.error("解析服务器ip为 %s 的 %s 监控文件的 cpu 数据出现异常,出现异常行数据为：%s" % (self.ip, self.name, line))
                error_num += 1
        self.cpu = round(cpu_sum / (len(lines) - error_num), 2)
        self.cpus = cpu_num_list
        logger.debug("cpu: %.2f%%" % self.cpu)
        logger.debug("监控到所有CPU数据:")
        logger.debug(self.cpus)

    def fetch_mem(self, lines):
        """
        获取 mem 的关键数据包括: 纯物理内存使用率, 包含虚拟内存的内存使用率(无则为0)
        :param lines: 带 mem 关键数据行
        """
        # 解析数据错误行数
        error_num = 0
        # 内存总负载
        mem_sum = float(0)
        # 虚拟内存总负载
        mem_virtual_sum = float(0)
        # 总内存监控数据
        mems_use = []
        # 空闲内存监控数据
        mems_free = []

        for line in lines:
            # NMON 文件中存在监控数据未与其他行分隔开
            # 判断当前数据行是否以 "MEM,T" 开头, 如果不是则分割
            index = line.find("MEM,T")
            if index != 0:
                line = line[index:-1]

            mems = line.split(",")
            if len(mems) == 17:
                # mem_use 实际使用内存 计算方式 (Memtotal - Memfree - cached - buffers)/Memtotal  * 100
                mem_use = (float(mems[2]) - float(mems[6]) - float(mems[11]) - float(mems[14])) / float(mems[2]) * 100
                mem_sum += mem_use

                mems_use.append(mem_use)
                mems_free.append(float(mems[6])/float(mems[2]) * 100)

            elif len(mems) == 8:
                #  mem_use 实际使用内存 计算方式 (Real total - Real free)/Real total * 100
                mem_use = (float(mems[6]) - float(mems[4])) / float(mems[6]) * 100
                mem_sum += mem_use

                # mem_virtual 包含虚拟内存使用时 计算方式
                # (Real total - Real free + Virtual total - Virtual free) /(Real total + Virtual total) * 100
                mem_virtual_sum += ((float(mems[6]) - float(mems[4]) + float(mems[7]) - float(mems[5])) / (
                            float(mems[6]) + float(mems[7])) * 100)

                mems_use.append(mem_use)
                mems_free.append(float(mems[4]) / float(mems[6]) * 100)

            else:
                logger.error("解析服务器ip为 %s 的 %s 监控文件的 MEM 数据出现异常,出现异常行数据为：%s" % (self.ip, self.name, line))
                error_num += 1

        self.mem = (round(mem_sum / (len(lines) - error_num), 2), round(mem_virtual_sum / (len(lines) - error_num), 2))
        self.mems.append(mems_use)
        self.mems.append(mems_free)
        logger.debug("mem: 不含虚拟内存的使用率 %.2f%%, 包含虚拟内存的使用率 %.2f%%" % (self.mem[0], self.mem[1]))
        logger.debug("总内存监控数据:")
        logger.debug(self.mems[0])
        logger.debug("空闲内存监控数据:")
        logger.debug(self.mems[1])

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

        disks_read = []
        disks_write = []
        disks_io = []
        disks_busy = []
        for line in lines:
            # NMON 文件中存在监控数据未与其他行分隔开
            # 判断当前数据行是否以 "DISK" 开头, 如果不是则分割
            index = line.find("DISK")
            if index != 0:
                line = line[index:-1]

            disks = line.split(",")
            if "DISKREAD,T" in line:
                # diskread
                disk_read_line_sum = float(0)
                # 统计每行之和
                for diskread_index in range(2, len(disks)):
                    disk_read_line_sum += float(disks[diskread_index])

                disks_read.append(disk_read_line_sum)
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

                disks_write.append(disk_write_line_sum)
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

                # 添加到监控数据中
                disks_io.append(disk_io_line_sum)
            elif "DISKBUSY,T" in line:
                # 获取 busi 每列初始值
                    # 计算 busi 每列均值
                    for disk_busy_line_index in range(2, len(disks)):
                        if diskbusy_num == 0:
                            diskbusy_avg.append(float(disks[disk_busy_line_index]))
                            disks_busy.append([float(disks[disk_busy_line_index])])
                        else:
                            diskbusy_avg[disk_busy_line_index - 2] = (float(
                                diskbusy_avg[disk_busy_line_index - 2]) * diskbusy_num + float(
                                disks[disk_busy_line_index])) / (diskbusy_num + 1)
                        disks_busy[disk_busy_line_index - 2].append(float(disks[disk_busy_line_index]))

                    diskbusy_num += 1

        # 获取 busi 最大列的均值
        for disk_busy in diskbusy_avg:
            if disk_busy > diskbusy_max:
                diskbusy_max = disk_busy

        diskbusy_max_index = diskbusy_avg.index(diskbusy_max)

        self.disks.append(disks_write)
        self.disks.append(disks_read)
        self.disks.append(disks_io)
        self.disks.append(disks_busy[diskbusy_max_index])

        logger.debug("DISK WRITE NMON DATA:")
        logger.debug(disks_write)
        logger.debug("DISK READ NMON DATA:")
        logger.debug(disks_read)
        logger.debug("DISK IO NMON DATA:")
        logger.debug(disks_io)
        logger.debug("DISK BUSY NMOM DATA:")
        logger.debug(disks_busy[diskbusy_max_index])


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
            # NMON 文件中存在监控数据未与其他行分隔开
            # 判断当前数据行是否以 "NET" 开头, 如果不是则分割
            index = line.find("NET")
            if index != 0:
                line = line[index:-1]

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
        try:
            logger.info("开始解析%s jmeter结果文件" % os.path.basename(file))
            super().file_analyse(file)
            file_all_path = file + r"\content\js\dashboard.js"
            with open(file_all_path, "r", encoding="utf8") as jmeterfile:
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
                        tmp_list = [tmp_data[1], round(float(tmp_data[10]), 2), tmp_data[3], round(float(tmp_data[4]), 2),
                                    round(float(tmp_data[5]), 2), round(float(tmp_data[6]), 2)]
                        # dict: {name:list}
                        self.result_dict[tmp_data[0]] = tmp_list

                    logger.debug("%s 提取结果 %s" % (os.path.basename(file), self.result_dict))

                else:
                    raise CustomError("%s获取压测结果失败,未找到匹配数据" % os.path.basename(file))
        finally:
            logger.info("%s jmeter 结果文件解析结束" % os.path.basename(file))


class LoadRunnerAnalyse(FileAnalyse):

    def __init__(self):
        super().__init__()
        self.result_dict = {}

    def file_analyse(self, file):
        """
        解析 Loadrunner 报告
        :param file: loadrunner 报告所在路径
        """
        try:
            logger.info("开始解析 %s loadrunner 报告" % os.path.basename(file))

            super().file_analyse(file)

            tps_list = []
            resp_avg_list = []
            resp_min_list = []
            resp_max_list = []

            summary_html_path = file + r'\An_Report1\summary.html'
            content_html_path = file + r'\An_Report1\contents.html'

            with open(summary_html_path, "r", encoding='utf8') as summary_html_file:
                summary_str = summary_html_file.read()
                transaction_name_list = re.findall(r'headers="LraTransaction Name".*?8">(.*?)</td>', summary_str)
                logger.debug("trasaction_name_list is None: %s" % str(False if(transaction_name_list is not None) else True))
                pass_list = re.findall(r'headers="LraPass".*?8">(.*?)</td>', summary_str)
                logger.debug("pass_list is None: %s" % str(False if (pass_list is not None) else True))
                fail_list = re.findall(r'headers="LraFail".*?8">(.*?)</td>', summary_str)
                logger.debug("fail_list is None: %s" % str(False if (fail_list is not None) else True))

            if not pass_list or not fail_list or not transaction_name_list:
                    raise CustomError("%s 有未匹配到的数据" % self.name)

            # TPS 从 TPS html 页面中获取, 先从 contents.html 获取到 TPS html 名称
            # Respnse Time 从 Response Time html 页面中获取,先从 contents.html 获取到 Response Time html 名称
            with open(content_html_path, "r", encoding='utf8') as content_html_file:
                content_str = content_html_file.read()
                tps_html_name_match = re.match(r'[\s\S]*href="(.*?)" Target.*?>Transactions per Second', content_str)
                response_time_html_name_match = re.match(r'[\s\S]*href="(.*?)" Target.*?>Average Transaction Response Time'
                                                         , content_str)

                if tps_html_name_match is None:
                    raise CustomError("%s 未找到 tps html 报告" % self.name)
                elif response_time_html_name_match is None:
                    raise CustomError("%s 未找到 Respnse Time html 报告" % self.name)

                tps_html_name = tps_html_name_match.group(1)
                logger.debug("%s tps html name %s " % (os.path.basename(file), tps_html_name))
                tps_html_path = file + r'\An_Report1' + os.path.sep + tps_html_name
                logger.debug("%s tps html path %s " % (os.path.basename(file), tps_html_path))
                response_time_html_name = response_time_html_name_match.group(1)
                logger.debug("%s response time html name %s" % (os.path.basename(file), response_time_html_name))
                response_time_html_path = file + r'\An_Report1' + os.path.sep + response_time_html_name
                logger.debug("%s response time html path %s" % (os.path.basename(file), response_time_html_path))

            self.fetch_tps(tps_html_path, tps_list)
            self.fetch_resp_time(response_time_html_path, resp_avg_list, resp_min_list, resp_max_list)

            # 长整数取到的数字带有逗号,例如1024是1,024,在取数字时,先将逗号去掉
            for index in range(0, len(transaction_name_list)):
                transaction_name = transaction_name_list[index]
                logger.debug("transaction name %s" % transaction_name)
                tps = tps_list[index]
                logger.debug("tps %s" % tps)
                pass_tsc = pass_list[index].replace(",", "")
                logger.debug("pass transaction: %s" % pass_tsc)
                fail_tsc = fail_list[index].replace(",", "")
                logger.debug("fail transaction: %s" % fail_tsc)
                # 时间转化成 ms 单位
                resp_avg = resp_avg_list[index]
                logger.debug("resp average time : %sms" % resp_avg)
                resp_max = resp_max_list[index]
                logger.debug("resp max time: %sms" % resp_max)
                resp_min = resp_min_list[index]
                logger.debug("resp min time: %sms" % resp_min)

                all_tsc = str(int(fail_tsc) + int(pass_tsc))
                error = round(int(fail_tsc)/int(all_tsc) * 100, 2)
                # list: [Transaction, TPS, Error%, Response Time(average), Response Time(min), Response Time(max)]
                data_list = [all_tsc, tps, error, resp_avg, resp_min, resp_max]
                # dict:{transaction name:list}
                self.result_dict[transaction_name] = data_list
        finally:
            logger.info("%s loadrunner 报告解析结束" % os.path.basename(file))

    def fetch_tps(self, file_path, tps_list):
        """
        提取 tps html 中 tps 的值
        :param file_path: tps html 绝对路径
        :param tps_list: 保存 tps 值的 list
        """
        logger.debug("%s 开始提取 tps 数据" % self.name)
        with open(file_path, "r", encoding='utf8') as tps_html_file:
            tps_str = tps_html_file.read()
            tps_table_list = re.findall(r'<tr class="legendRow">([\s\S]*?)</tr>', tps_str)

            if not tps_table_list:
                raise CustomError("%s 未匹配到 tps 数据" % self.name)

            logger.debug("%s 共匹配到 %d 条tps记录" % (self.name, len(tps_table_list)))
            for index in range(0, len(tps_table_list)):
                tps_table_str = tps_table_list[index].replace("\n", "")
                tps_data_list = tps_table_str.split("<td>", 5)

                # 判断是否为成功记录,成功记录提取数据, 失败记录跳过
                if tps_data_list[2][:-5].split(":")[1] != "Pass":
                    continue

                logger.debug("%s 交易 transaction %s tps %s" % (
                    self.name, tps_data_list[2][:-5].split(":")[0], tps_data_list[4][:-5]))

                tps_list.append(tps_data_list[4][:-5])

    def fetch_resp_time(self, file_path, resp_avg_list, resp_min_list, resp_max_list):
        """
        提取 response time html 中 各 response time 的值
        :param file_path: response time html 绝对路径
        :param resp_avg_list: 保存 response time average 值
        :param resp_min_list: 保存 response time min 值
        :param resp_max_list: 保存 response time max 值
        """
        logger.debug("%s 开始提取 response time 数据" % self.name)
        with open(file_path, "r", encoding='utf8') as response_time_html_file:
            response_time_str = response_time_html_file.read()
            response_time_table_list = re.findall(r'<tr class="legendRow">([\s\S]*?)</tr>', response_time_str)

            if not response_time_table_list:
                raise CustomError("%s 未匹配到 response time 数据" % self.name)

            logger.debug("%s 共匹配到 %d 条 response time 记录" % (self.name, len(response_time_table_list)))
            for index in range(0, len(response_time_table_list)):
                response_time_table_str = response_time_table_list[index].replace("\n", "")
                response_time_data_list = response_time_table_str.split("<td>", 6)

                trasaction_name = response_time_data_list[2][:-5]
                # 单位转化为 ms
                response_time_average = round(float(response_time_data_list[4][:-5]) * 1000, 2)
                logger.debug("%s 交易 transcation %s response time average: %.2fms" % (
                    self.name, trasaction_name, response_time_average))
                resp_avg_list.append(response_time_average)

                response_time_min = round(float(response_time_data_list[3][:-5]) * 1000, 2)
                logger.debug("%s 交易 transcation %s response time min: %.2fms" % (
                    self.name, trasaction_name, response_time_min))
                resp_min_list.append(response_time_min)

                response_time_max = round(float(response_time_data_list[5][:-5]) * 1000, 2)
                logger.debug("%s 交易 transcation %s response time max: %.2fms" % (
                    self.name, trasaction_name, response_time_max))
                resp_max_list.append(response_time_max)


if __name__ == "__main__":
    # nmonfile = r'D:\work\工具\nmon\71Vusr.nmon'
    # nmonfile = r'C:\Users\zengjn22046\Desktop\大额贷记往账1Vuser.nmon'
    # nmon = NmonAnalyse()
    # nmon.file_analyse(nmonfile)
    # print(nmon.cpu)
    # print(nmon.mem)
    # print(nmon.disk)
    # print(nmon.net)
    jmetrfile = r"C:\Users\zengjn22046\Desktop\yecxwz50"
    jmeter = JmeterAnalyse()
    jmeter.file_analyse(jmetrfile)
    # loadrunner_file = r'C:\Users\zengjn\Desktop\Get\scenario\res'
    # loadrunner = LoadRunnerAnalyse()
    # loadrunner.file_analyse(loadrunner_file)
    # print(loadrunner.result_dict)