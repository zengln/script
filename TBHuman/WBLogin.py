# -*- coding:utf-8 -*-

import re
import rsa
import time
import json
import random
import base64
import binascii
import urllib.parse
import urllib.request

from http import cookiejar
from PIL import Image

class WBHuman():

    def __init__(self, name, passwd):
        self.name = name
        self.passwd = passwd
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'
        }

    def get_encode_name(self):
        encode_name = base64.b64encode(self.name.encode('utf-8'))
        return encode_name

    def enable_cookie(self):
        cookie = cookiejar.CookieJar()
        handler = urllib.request.HTTPCookieProcessor(cookie)
        opener = urllib.request.build_opener(handler)
        urllib.request.install_opener(opener)

    def pre_login(self):
        pre_login_url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su='
        pre_login_url = pre_login_url + urllib.request.quote(self.get_encode_name())
        pre_login_url = pre_login_url + '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_='
        pre_login_url = pre_login_url + str(int(time.time()*1000))

        request = urllib.request.Request(pre_login_url)
        response = urllib.request.urlopen(request)

        data = response.read().decode('utf-8')

        pattern = re.compile('\((.*?)\)')
        return_data = re.search(pattern, data).group(1)

        return json.loads(return_data)

    def get_encode_passwd(self, data):

        '''
        :func  对密码进行加密

        :param data: 预登录返回的数据

        :return: 加密后的密码
        '''

        rsa_e = int('10001', 16)
        rsa_n = int(data['pubkey'], 16)
        key = rsa.PublicKey(rsa_n, rsa_e)
        message = str(data['servertime']) + '\t' + str(data['nonce']) + '\n' + str(self.passwd)
        sp = rsa.encrypt(message.encode('utf-8'), key)
        return binascii.b2a_hex(sp)

    def loging(self, data):
        login_url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        post_data = urllib.parse.urlencode(data).encode('utf-8')
        request = urllib.request.Request(login_url, headers=self.headers, data=post_data)
        response = urllib.request.urlopen(request)
        return response.read().decode('GBK')


    def build_post_data(self, data):
        print(data)
        post_data = {
            "entry": "weibo",
            "gateway": "1",
            "from": "",
            "savestate": "0",
            "qrcode_flag": 'false',
            "useticket": "1",
            "pagerefer": "",
            "vsnf": "1",
            "su": self.get_encode_name(),
            "service": "miniblog",
            "servertime": data['servertime'],
            "nonce": data['nonce'],
            "pwencode": "rsa2",
            "rsakv": data['rsakv'],
            "sp": self.get_encode_passwd(data),
            "sr": "1680*1050",
            "encoding": 'UTF-8',
            "prelt": "194",
            "url": "https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
            "returntype": "META"
        }
        return post_data

    def door_input(self, html, pcid, data):
        if "/ajaxlogin" in html:
            door_url = "https://login.sina.com.cn/cgi/pin.php?r="
            door_url = door_url + str(int(random.random() * 100000000)) + "&s=0&p="
            door_url = door_url + pcid
            request = urllib.request.Request(door_url, headers=self.headers)
            door_page = urllib.request.urlopen(request)
            with open("door.jpg", 'wb') as f:
                f.write(door_page.content)
                f.close()
            try:
                im = Image.open('door.jpg')
                im.show()
                im.close()
            except:
                print("请在当前目录下寻找验证码并输入")

            data['door'] = input("请输入验证码")
            data['pcid'] = pcid

            html = self.loging(data)
            return html

        return None


    def login(self):
        self.enable_cookie()
        json_data = self.pre_login()
        post_data = self.build_post_data(json_data)
        html = self.loging(post_data)

        html_door = self.door_input(html, json_data['pcid'], post_data)

        if html_door != None:
            html = html_door

        pattern = re.compile('location\.replace\("(.*?)"\)')
        redirect_url = re.search(pattern, html).group(1)
        request = urllib.request.Request(redirect_url, headers=self.headers)
        response = urllib.request.urlopen(request)
        html2 = response.read().decode('GBK')

        pattern2 = re.compile('location\.replace\(\'(.*?)\'\)')
        redirect_url2 = re.search(pattern2, html2).group(1)
        request3 = urllib.request.Request(redirect_url2, headers=self.headers)
        response = urllib.request.urlopen(request3)
        html3 = response.read().decode('utf-8')

        pattern3 = re.compile(r'"userdomain":"(.*?)"')
        final_url = re.search(pattern3, html3).group(1)

        final_url = "https://weibo.com/" + final_url
        final_request = urllib.request.Request(final_url, headers=self.headers)
        response = urllib.request.urlopen(final_request)
        print(response.read().decode('utf-8'))


wb = WBHuman('admin', '123456')
wb.login()



