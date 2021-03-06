# -*- coding:utf-8 -*-
# @Time    : 2020/5/21 15:17
# @Author  : zengln
# @File    : urls.py

from django.urls import path, re_path
from transcode import views

urlpatterns = [
    path('', views.index),
    path('<int:transcode>/', views.trans_code, name='trans_code'),
    path('<int:transcode>/node_set', views.node_set, name="node_set"),
]