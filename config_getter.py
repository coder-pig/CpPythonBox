# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : config_getter.py
   Author   : CoderPig
   date     : 2023-01-30 14:43 
   Desc     : 读取配置文件配置
-------------------------------------------------
"""
import configparser
import os
import os.path

from util.logger_util import default_logger

logger = default_logger()


def get_config(key, section='config'):
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.split(os.path.realpath(__file__))[0], 'config.ini'), encoding='utf8')
    return config.get(section, key)


if __name__ == '__main__':
    print(get_config("video_subtitle_host"))
