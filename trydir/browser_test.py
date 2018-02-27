# -*- coding:utf-8 -*-

# author: zengln
# create: 2018-02-27
# 一个 selenium + chromeDriver 的尝试

import os
from selenium import webdriver

# 引入 chromedriver.exe
chromedriver = "D:\python3\Scripts\chromedriver.exe"

os.environ["webdriver.chrome.driver"] = chromedriver
browser = webdriver.Chrome(chromedriver)

# 设置浏览器需要打开的 url
url = "https://weibo.com/"
browser.get(url)

# 隐式等待
browser.implicitly_wait(10)
browser.find_element_by_id("loginname").send_keys("username")
browser.find_element_by_name("password").send_keys("password")
# browser.find_element_by_id("su").click()
browser.find_element_by_class_name("btn_32px").click()
# 关闭浏览器
# browser.quit()