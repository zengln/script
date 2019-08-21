# -*- coding:utf-8 -*-

import os

cmd_lr = r'C:\"Program Files (x86)"\HP\LoadRunner\bin\wlrun -TestPath  C:\Users\zeng\Desktop\Get\scenario\Scenario-5.lrs -Run -ResultName C:\Users\zeng\Desktop\Get\scenario\res-5'

cmd_jmeter = r'D:\JMeter\apache-jmeter-5.1.1\bin\jmeter -n -t C:\Users\zeng\Desktop\test.jmx -l C:\Users\zeng\Desktop\test.jtl'

# os.system(cmd)
p = os.popen(cmd_jmeter)
print(p.read())


