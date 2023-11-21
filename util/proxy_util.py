# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : proxy_util.py
   Author   : CoderPig
   date     : 2023-11-21 17:38
   Desc     : 代理工具类
-------------------------------------------------
"""
from config_getter import get_configs

# 小象代理隧道
proxyHost = "http-short.xiaoxiangdaili.com"  # 代理隧道服务器
proxyPort = "10010"  # 代理隧道端口

config_tuple = get_configs('xx-dl', ('proxy_user', 'proxy_pass'))

# 代理隧道验证信息
proxyUser = config_tuple[0]
proxyPass = config_tuple[1]

proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
    "host": proxyHost,
    "port": proxyPort,
    "user": proxyUser,
    "pass": proxyPass,
}

proxies = {
    "http": proxyMeta,
    "https": proxyMeta,
}


# 获得默认代理
def get_proxies():
    return proxies
