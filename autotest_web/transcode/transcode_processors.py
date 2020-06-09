# -*- coding:utf-8 -*-
# @Time    : 2020/6/9 10:25
# @Author  : zengln
# @File    : transcode_processors.py

from transcode.models import Node
from django.db.models import Count


def trans_code_list(request):
    nodes = Node.objects.values('trans_code').annotate(counts=Count('trans_code'))
    return {"nodes": nodes}
