#### 2018-02-27

selenium + chromedriver 模拟浏览器登录微博

#### 2018-02-28

更新自动发动态。
唯一要注意的一点是设置好延时 , 给 browser 获取 cookie 的时间。在点击登录按钮后 , 立刻再请求主页面则是不带 cookie 的browser 发起请求。相当于没有进行登录

#### 2018-03-14

添加将 word 文档中的接口转化为 xml 的脚本

#### 2018-03-22

添加一个自动生成指定长度字符串的小工具

#### 2018-05-23

添加通过 python 调用 excel 宏解析 nmon 文件脚本

#### 2019-08-02
添加远程下载nmon文件类

### 2019-08-04
新增读取控制文件类
将运行Excel进程转为不可见
新增nmon_analyse.py文件
NmonResult.py将结果文件第一行保存为标题,数据从第二行开始写入

### 2019-08-05
新增处理AIX系统,MEM数据计算问题
配置文件新增参数
nmon_analyse 新增下载代码
SSHSocket 类调整

### 2019-08-06
修改nmon_analyse, 将下载与处理 nmon 逻辑串起来

修改nmon_analyse, 新增对非法下载标识的处理

修改nmon_analyse, 制定error.log 文件编码为 UTF-8

修改 ExcelMirco.py, 调整参数

修改NmonResult.py, 将结果中的 cpu 数据与内存数据存为保留两位小数的百分数

新增按任意键退出程序,方便在 CMD 下查看报错信息

### 2019-08-07
修改nmon_analyse,修改程序正常结束,不需要退出程序提示, 只有异常被抛出时,需要保持 CMD 窗口
