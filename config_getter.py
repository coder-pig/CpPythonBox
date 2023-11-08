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
config_file = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'config.ini')


def get_config(key, section='config'):
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf8')
    return config.get(section, key)


def get_configs(section='config', key_args=()):
    """
    获取多个配置项的元组
    :param section: 配置块名称
    :param key_args: 配置key
    :return:
    """
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf8')
    result_tuple = tuple(config.get(section, key) for key in key_args) if key_args else ()
    return result_tuple


def update_configs(section='config', key_value_dict=dict):
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf8')
    for key, value in key_value_dict.items():
        config.set(section, key, value)
    config.write(open(config_file, 'w+', encoding='utf8'))


def update_config(key, value, section='config'):
    config = configparser.ConfigParser()
    config.read(config_file, encoding='utf8')
    config.set(section, key, value)
    config.write(open(config_file, 'w+', encoding='utf8'))


if __name__ == '__main__':
    print(get_config("video_subtitle_host"))
