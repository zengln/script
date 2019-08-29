# -*- coding:utf-8 -*-

import os
import subprocess
from performance_autotest.customexception import CustomError
from performance_autotest.log import logger


__all__ = ["get_all_script", "jmeter_cmd", "lr_cmd", "exe_command"]


def get_all_script(script_path, file_extension):
    """
    获取当前文件夹下所有指定后缀文件
    :param script_path:    文件夹路径
    :param file_extension: 文件类型
    :return:返回脚本文件列表
    """
    script_files = []
    if not os.path.exists(script_path):
        raise CustomError("路径错误,文件夹不存在")

    files = os.listdir(script_path)
    logger.debug("当前路径"+script_path+"下所有文件与文件夹")
    logger.debug(files)
    for file in files:
        if not os.path.isfile(script_path + "\\" + file):
            continue
        if os.path.splitext(file)[1] == file_extension:
            script_files.append(os.path.splitext(file)[0])

    if not script_files.__len__():
        raise CustomError("路径下无后缀为%s的脚本文件" % file_extension)

    logger.debug("所有脚本文件")
    logger.debug(script_path)
    return script_files


def jmeter_cmd(script_file, path):
    """
    获取路径生成执行脚本命令
    """
    cmd_list = []
    # TODO cmd 参数化
    cmd = r"D:\JMeter\apache-jmeter-5.1.1\bin\jmeter -n -t "
    # cmd = r"jmeter -n -t "
    for file in script_file:
        command = cmd + path + os.path.sep + file + ".jmx" + " -l " + path + os.path.sep + file + ".jtl"
        cmd_list.append(command)

    logger.debug("生成的 jmeter 命令")
    logger.debug(cmd_list)
    return cmd_list


def lr_cmd(script_file, path):
    """
    获取路径生成执行脚本命令
    """
    cmd_list = []
    # TODO cmd 参数化
    cmd = r'C:\"Program Files (x86)"\HP\LoadRunner\bin\wlrun -TestPath  '
    for file in script_file:
        command = cmd + path + os.path.sep + file + ".lrs" + " -Run -ResultName " + path + os.path.sep + file
        cmd_list.append(command)

    logger.debug("生成的 lr 命令")
    logger.debug(cmd_list)
    return cmd_list


def exe_commands(commands):
    for command in commands:
        logger.debug("正在执行命令:"+command)
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if not result.returncode:
            logger.info(result.stdout.decode("gbk"))
        else:
            # 调用 lr 时,会抛出一个 log4cxx 的异常, 但是脚本正常跑完,结果保存成功,此异常暂时忽略
            err_msg = result.stderr.decode('gbk')
            if err_msg.find("log4cxx") >= 0:
                continue
            raise CustomError(err_msg)


def exe_command(command):
    logger.debug("正在执行命令:"+command)
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if not result.returncode:
        logger.info(result.stdout.decode("gbk"))
    else:
        # 调用 lr 时,会抛出一个 log4cxx 的异常, 但是脚本正常跑完,结果保存成功,此异常暂时忽略
        err_msg = result.stderr.decode('gbk')
        if not err_msg.find("log4cxx") >= 0:
            raise CustomError(err_msg)


if __name__ == '__main__':
    lr_path = r"C:\Users\zengjn\Desktop\Get\scenario"
    jmeter_path = r'C:\Users\zengjn\Desktop\jemter'
    files_jmeter = get_all_script(jmeter_path, ".jmx")
    jmeter_command = jmeter_cmd(files_jmeter, jmeter_path)
    print("lr=============================")
    lr_files = get_all_script(lr_path, ".lrs")
    lr_command = lr_cmd(lr_files, lr_path)
    exe_commands(lr_command)
