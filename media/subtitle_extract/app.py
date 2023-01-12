# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : app.py
   Author   : CoderPig
   date     : 2023-01-12 10:34 
   Desc     : 字幕提取工具
-------------------------------------------------
"""
import os
from util.file_util import search_all_file, is_dir_existed
from util.logger_util import default_logger

logger = default_logger()

res_dir = os.path.join(os.getcwd(), "res")  # 资源文件存放目录
origin_dir = os.path.join(res_dir, "origin")  # 把要转换的文件放在此目录中
temp_dir = os.path.join(res_dir, "origin")  # 中间产物路径
result_dir = os.path.join(res_dir, "result")  # 最终产物输出路径


def init():
    is_dir_existed(res_dir)
    is_dir_existed(origin_dir)
    is_dir_existed(temp_dir)
    is_dir_existed(result_dir)


if __name__ == '__main__':
    logger.info("检索路径 → %s" % origin_dir)
    media_file_list = search_all_file(origin_dir, target_suffix_tuple=(
        '.mp3', '.wav', ".mp4", ".flv", ".avi", ".ts", ".wmv", ".mkv", ".mpeg"))
    if len(media_file_list) == 0:
        logger.info("待处理音视频为空，请检测后重试...")
        exit(1)
    else:
        logger.info("检索到下述音视频：\n {}".format("=" * 64))
        for pos, media_file in enumerate(media_file_list):
            logger.info("{} → {}".format(pos, media_file))
