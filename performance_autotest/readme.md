#### 20190820
flask新增一个简单的接口

#### 20190821
windows上使用命令行运行Loadrunner 场景与 jmeter 脚本

#### 20190822
新增自定义异常

自动拼接生成命令

#### 20190826
subprocess 模块替换os.system

增加server.py

增加config.ini文件

lr调用异常log4cxx做特殊处理

Rconfig部分配置设置默认值

server拼接nmon命令

#### 20190827
整合场景运行与连接后台开启nmon监控

#### 20190829
nmon监控支持服务器集群

增加全局log模块

增加debug开关

#### 20190905
新增 nmon 文件解析

#### 20190906
新增 jmeter 结果解析

#### 20190909
添加jmeter报告文件解析,jmeter5.1版本后才存在statistics.json文件,因此数据提取改为从js文件中提取。并添加运行日志

修改script 中 jmeter命令,在执行完成后生成自动生成报告

#### 20190910
添加loadrunner报告解析

#### 20190911
Server类增加属性 file_list，保存下载nmon文件全路径
resultdata 修改几个需要比较值的列,第一列的值转为float。防止后续进行比较时出现异常
script, server 优化log显示，增加loadrunner解析命令,保存压测结果文件存放路径

#### 20190912
修改 loadrunner 报告提取逻辑
新增report生成
resultdata 增加ip属性,优化nmon数据格式
整合report到主流程中