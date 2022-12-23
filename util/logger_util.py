# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : logger_util.py
   Author   : CoderPig
   date     : 2022-12-23 10:01 
   Desc     : 日志工具类
-------------------------------------------------
"""
import logging


# 默认日志工具
def default_logger():
    custom_logger = logging.getLogger("CpPythonBox")
    if not custom_logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            fmt='%(asctime)s %(process)d:%(processName)s- %(levelname)s === %(message)s',
            datefmt="%Y-%m-%d %H:%M:%S %p"))
        custom_logger.addHandler(handler)
        custom_logger.setLevel(logging.INFO)
    return custom_logger


if __name__ == '__main__':
    logger = default_logger()
    logger.info("测试")
