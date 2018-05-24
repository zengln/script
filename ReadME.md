### 1. Nmon 模块

nmon 模块是一个可以自动调用宏程序解析 nmon 文件, 并提取常用监控数据的模块。

### 2. Nmon 类用法

```
# 宏文件路径
MicroFilePath = "C:\\Users\user\Desktop\\nmon analyser v46.xlsm"
# 待解析的 nmon 文件路径的数组
nmon_tuple = [r"C:\Users\user\Desktop\70Vusr.nmon", r"C:\Users\user\Desktop\71Vusr .nmon"]
# 解析结果文件保存路径(此参数仅在待解析文件只有一个的时候生效)
Path = r"D:\db.xls"
# 调用 Micro 宏, 解析 nmon 文件, 返回结果文件路径数组
result = ExcelMicro.get_nmon_result_file(MicroFilePath, nmon_tuple, Path)
# 传入结果文件路径数组
nr = NmonResult.NmonResult(result)
# 对数组中路径所指向的 excel 文件进行数据提取, 并保存结果,
# 结果保存在 C 盘根目录的一个叫 test 的一个 excel 中
nr.get_file()
# 如果有额外的数据需求, 可以通过该方法获取数据
data = nr.get_cell_value(nr.get_work_book(), "CPU", 1, 1)
# 再通过次方法写入指定 excel 中
nr.write_excel(r'C:\test.xls', "sheet1", 0, 5, data)
```

