# -*- coding:utf-8 -*-

# author: zengln
# create: 2018-02-27
# 一个 selenium + chromeDriver 的尝试

import os
import time
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
browser.find_element_by_class_name("btn_32px").click()

time.sleep(5)
browser.get("https://weibo.com/")

browser.implicitly_wait(10)
browser.find_elements_by_class_name("W_input")[1].send_keys("Hello Selenium")
browser.find_element_by_class_name("btn_30px").click()

# 关闭浏览器
# browser.quit()