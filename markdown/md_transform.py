# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : md_transform.py
   Author   : CoderPig
   date     : 2023-01-06 14:44 
   Desc     : md文件转换
-------------------------------------------------
"""
import asyncio
from functools import partial

from util.download_util import download_pic
from util.file_util import is_dir_existed, search_all_file, read_file_text_content, write_text_to_file
from util.logger_util import default_logger
import os
import re
import time

logger = default_logger()
origin_md_dir = os.path.join(os.getcwd(), "origin_md")  # 原始md文件目录
local_md_dir = os.path.join(os.getcwd(), "local_md")  # 本地md文件目录
server_md_dir = os.path.join(os.getcwd(), "server_md")  # 转换成自己的图片服务器md文件目录
pic_match_pattern = re.compile(r'(\]: |\()+(http.*?\.(png|PNG|jpg|JPG|gif|GIF|webp|svg|SVG))', re.M)  # 匹配图片的正则
order_set = {i for i in range(1, 50000)}  # 避免图片名重复后缀


# 检索md文件
def retrieve_md(file_dir):
    logger.info("检索路径【%s】" % file_dir)
    md_file_list = search_all_file(file_dir, target_suffix_tuple=('md', "MD"))
    if len(md_file_list) == 0:
        logger.info("未检测到Markdown文件，请检查后重试!")
        exit(-1)
    else:
        logger.info("检测到MD文件【%d】个，请输入文件序号后回车转换 (直接回车代表处理所有文件)" % len(md_file_list))
        for pos, md_file in enumerate(md_file_list):
            logger.info("%d、%s" % (pos, md_file))
        choose_input = input()
        if len(choose_input) == 0:
            process_md(md_file_list)
        else:
            if choose_input.isdigit() and 0 <= int(choose_input) < len(md_file_list):
                process_md([md_file_list[int(choose_input)]])
            else:
                logger.info("输入错误，请输入正确的文件序号!")
                exit(-1)


# 处理文件列表
def process_md(file_list):
    logger.info("仅生成本地md文件吗？1、是 2、否 (顺带转换成自己的图片服务器md文件目录)")
    choose_input = input()
    if choose_input.isdigit():
        if int(choose_input) == 1:
            for file in file_list:
                to_local_md(file)
        elif int(choose_input) == 2:
            pass
    else:
        logger.info("请输入正确的选项!")
        exit(-1)


# 转换成本地MD
def to_local_md(md_file):
    logger.info("处理文件：【%s】" % md_file)
    # 获取md文件名
    md_file_name = md_file.split(os.sep)[-1].replace(".md", "").replace(" ", "")
    # 生成文件夹，及存图片的pic文件夹
    md_file_dir = os.path.join(local_md_dir, md_file_name)
    md_pic_dir = os.path.join(md_file_dir, "images")
    md_file_path = os.path.join(md_file_dir, md_file_name + ".md")
    is_dir_existed(md_file_dir)
    is_dir_existed(md_pic_dir)
    # 读取md文件内容
    old_content = read_file_text_content(md_file)
    new_content = pic_match_pattern.sub(partial(pic_to_local, pic_save_dir=md_pic_dir), old_content)
    # 生成新的md文件
    write_text_to_file(new_content, md_file_path)
    logger.info("处理完毕，生成新md文件：{}".format(md_file_path))


# 远程图片转换为本地图片
def pic_to_local(pic_url, pic_save_dir):
    # 获取图片后缀
    pic_suffix = os.path.splitext(pic_url.group(2))[-1]
    # 生成本地图片名
    img_file_name = "{}_{}{}".format(int(round(time.time())), order_set.pop(), pic_suffix)
    # 图片项目路径(md文件用到)
    relative_path = 'images/{}'.format(img_file_name)
    # 图片绝对路径
    absolute_path = os.path.join(pic_save_dir, img_file_name)
    # 异步下载图片
    asyncio.run(process_download_pics(absolute_path, pic_url.group(2)))
    return relative_path


# 异步方法
async def process_download_pics(pic_path, url):
    await download_pic(pic_path, url)


# 转换成自己的图片服务器md文件
def to_server_md(md_file):
    pass


if __name__ == '__main__':
    is_dir_existed(origin_md_dir)
    is_dir_existed(local_md_dir)
    is_dir_existed(server_md_dir)
    retrieve_md(origin_md_dir)

