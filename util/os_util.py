# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : os_util.py
   Author   : CoderPig
   date     : 2022-12-23 10:04 
   Desc     : 
-------------------------------------------------
"""
import sys


# 判断是否为mac
def is_mac():
    return sys.platform.startswith('darwin')


# 判断是否为windows
def is_win():
    return sys.platform.startswith('win')
