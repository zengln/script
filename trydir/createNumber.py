# -*- coding:utf-8 -*-

# create:2018-03-22
# author:zengln
# desc:  指定字符数量,随机生成指定数量的字符

import random
import string

class createString(object):

    def __init__(self):
        pass

    def randstring(self, num):
        return ''.join(random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)for _ in range(num))
