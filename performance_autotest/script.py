# -*- coding:utf-8 -*-

import os
import subprocess
from performance_autotest.customexception import CustomError
from performance_autotest.log import logger


__all__ = ["get_all_script", "jmeter_cmd", "lr_cmd", "exe_command", "get_all_script_path","analyse_lr_cmd"]


def get_all_script(script_path, file_extension):
    """
    获取当前文件夹下所有指定后缀文件
    :param script_path:    文件夹路径
    :param file_extension: 文件类型
    :return:返回脚本文件列表
    """
    # 如果是一个文件,判断后缀是否合法后,返回
    if os.path.isfile(script_path):
        if os.path.splitext(script_path)[1] == file_extension:
            return [os.path.split(script_path)[1]]
        else:
            raise CustomError("检查到文件后缀与脚本类型不符, 预期脚本类型为: %s" % file_extension)

    script_files = []
    if not os.path.exists(script_path):
        raise CustomError("路径错误,文件夹或者文件不存在: %s" % script_path)

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
    logger.debug(script_files)
    return script_files


def get_all_script_path(file_path, file_extension):
    """
    获取当前文件夹下所有制定后缀文件
    :param file_path:       文件夹路径
    :param file_extension:  文件类型
    :return:返回脚本文件全路径列表
    """
    files_path = []
    for root, dirs, files in os.walk(file_path):
        for file in files:
            logger.debug("文件名："+file)
            if os.path.splitext(file)[1] == file_extension:
                file_path = os.path.join(root, file)
                logger.info("含有"+file_extension+"后缀的文件:"+file+",全路径为:"+file_path)
                files_path.append(os.path.splitext(file_path)[0])

    return files_path


def analyse_lr_cmd(files_path):
    """
    生成lr解析命令
    """
    cmd_anaylise_list = []
    cmd = r'wlrun -TestPath '
    # cmd_analyse = r'C:\"Program Files (x86)"\HP\LoadRunner\bin\AnalysisUI -RESULTPATH '
    cmd_analyse = r'AnalysisUI -RESULTPATH '
    for file_path in files_path:
        command_analyse = cmd_analyse + file_path + ".lrr -TEMPLATENAME html"
        cmd_anaylise_list.append(command_analyse)

    logger.debug("生成的 lr 解析命令")
    logger.debug(cmd_anaylise_list)
    return cmd_anaylise_list


def jmeter_cmd(script_file, path):
    """
    获取路径生成执行脚本命令
    """
    cmd_list = []
    result_file_list = []
    # cmd = r"D:\JMeter\apache-jmeter-5.1.1\bin\jmeter -n -t "
    cmd = r"jmeter -n -t "
    for file in script_file:
        command = cmd + path + os.path.sep + file + ".jmx" + " -l " + path + os.path.sep + file + ".jtl -e -o " \
                  + path + os.path.sep + file
        cmd_list.append(command)
        result_file_list.append(path + os.path.sep + file)

    logger.debug("生成的 jmeter 命令")
    logger.debug(cmd_list)
    logger.debug(("jmeter结果文件保存路径"))
    logger.debug(result_file_list)
    return cmd_list, result_file_list


def lr_cmd(script_file, path):
    """
    获取路径生成执行脚本命令
    """
    cmd_list = []
    cmd_anaylise_list = []
    result_file_list = []
    # cmd = r'C:\"Program Files (x86)"\HP\LoadRunner\bin\wlrun -TestPath  '
    cmd = r'wlrun -TestPath '
    # cmd_analyse = r'C:\"Program Files (x86)"\HP\LoadRunner\bin\AnalysisUI -RESULTPATH '
    cmd_analyse = r'AnalysisUI -RESULTPATH '
    for file in script_file:
        command = cmd + path + os.path.sep + file + ".lrs" + " -Run -ResultName " + path + os.path.sep + file
        command_analyse = cmd_analyse + path + os.path.sep + file + os.path.sep + file + ".lrr -TEMPLATENAME html"
        cmd_list.append(command)
        cmd_anaylise_list.append(command_analyse)
        result_file_list.append(path + os.path.sep + file)

    logger.debug("生成的 lr 命令")
    logger.debug(cmd_list)
    logger.debug("生成的 lr 解析命令")
    logger.debug(cmd_anaylise_list)
    logger.debug("loadrunner 结果文件保存路径")
    logger.debug(result_file_list)
    return cmd_list, cmd_anaylise_list, result_file_list


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
    print(get_all_script(r"D:\CDRDT_20_12.lrs", ".lrs"))

