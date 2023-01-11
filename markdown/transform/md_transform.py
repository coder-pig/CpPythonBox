# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : md_transform.py
   Author   : CoderPig
   date     : 2023-01-06 14:44 
   Desc     : md文件转换
            使用方法：将要转换的md文件放到origin_md目录下，然后运行即可自动转换
            如果用到生成doc的功能，需要电脑先安装一下pandoc，下载地址：https://github.com/jgm/pandoc/releases
-------------------------------------------------
"""
import asyncio
from functools import partial

from util.adb_util import start_cmd
from util.download_util import download_pic
from util.file_util import is_dir_existed, search_all_file, read_file_text_content, write_text_to_file
from util.logger_util import default_logger
import os
import re
import time

logger = default_logger()
origin_md_dir = os.path.join(os.getcwd(), "origin_md")  # 原始md文件目录
local_md_dir = os.path.join(os.getcwd(), "local_md")  # 本地md文件目录
local_doc_dir = os.path.join(os.getcwd(), "local_doc")  # 本地doc文件目录
server_md_dir = os.path.join(os.getcwd(), "server_md")  # 转换成自己的图片服务器md文件目录
pic_match_pattern = re.compile(r'(\]: |\()+(http.*?\.(png|PNG|jpg|JPG|gif|GIF|svg|SVG|webp|awebp))\??(\)?)',
                               re.M)  # 匹配图片的正则
order_set = {i for i in range(1, 500000)}  # 避免图片名重复后缀
generate_server_md = False  # 是否在本地化后生成为自己图床的md文件
generate_doc = True  # 是否在本地化后生成doc文件


# 检索md文件
def retrieve_md(file_dir):
    logger.info("检索路径 → %s" % file_dir)
    md_file_list = search_all_file(file_dir, target_suffix_tuple=('md', "MD"))
    if len(md_file_list) == 0:
        logger.info("未检测到Markdown文件，请检查后重试!")
        exit(-1)
    else:
        logger.info("检测到Markdown文件 → %d个" % len(md_file_list))
        logger.info("=" * 64)
        for pos, md_file in enumerate(md_file_list):
            logger.info("%d、%s" % (pos + 1, md_file))
        logger.info("=" * 64)
        logger.info("执行批处理操作")
        process_md(md_file_list)


# 处理文件列表
def process_md(file_list):
    for file in file_list:
        to_local_md(file)


# 转换成本地MD
def to_local_md(md_file):
    logger.info("处理文件：【%s】" % md_file)
    # 获取md文件名
    md_file_name = os.path.basename(md_file)
    # 生成md文件的目录、图片目录，doc目录
    new_md_dir = os.path.join(local_md_dir, md_file_name[:-3])
    new_picture_dir = os.path.join(new_md_dir, "images")
    is_dir_existed(new_md_dir)
    is_dir_existed(new_picture_dir)
    # 生成md文件路径
    new_md_file_path = os.path.join(new_md_dir, md_file_name)
    new_doc_file_path = os.path.join(local_doc_dir, md_file_name[:-3].replace("知乎盐选 ", "") + ".docx")
    # 读取md文件内容
    old_content = read_file_text_content(md_file)
    # 替换原内容
    new_content = pic_match_pattern.sub(partial(pic_to_local, pic_save_dir=new_picture_dir), old_content)
    # 生成新的md文件
    write_text_to_file(new_content, new_md_file_path)
    logger.info("新md文件已生成 → {}".format(new_md_file_path))
    # 生成新的doc文件
    if generate_doc:
        os.chdir(new_md_dir)
        start_cmd('pandoc "{}" -o "{}"'.format(new_md_file_path, new_doc_file_path))
        logger.info("新doc文件已生成 → {}".format(new_doc_file_path))
    logger.info("=" * 64)
    if generate_server_md:
        to_server_md(new_md_file_path)


# 远程图片转换为本地图片
def pic_to_local(match_result, pic_save_dir):
    logger.info("替换前的图片路径：{}".format(match_result[2]))
    # 生成新的图片名
    img_file_name = "{}_{}.{}".format(int(round(time.time())), order_set.pop(), match_result[3])
    # 拼接图片相对路径(Markdown用到的)
    relative_path = 'images/{}'.format(img_file_name)
    # 拼接图片绝对路径，下载到本地
    absolute_path = os.path.join(pic_save_dir, img_file_name)
    logger.info("替换后的图片路径：{}".format(relative_path))
    # 顺带下载图片
    loop.run_until_complete(download_pic(absolute_path, match_result[2]))
    # 还需要拼接前后括号()
    return "{}{}{}".format(match_result[1], relative_path, match_result[4])


# 异步方法
async def process_download_pics(pic_path, url):
    await download_pic(pic_path, url)


# 转换成自己的图片服务器md文件
def to_server_md(md_file):
    pass


if __name__ == '__main__':
    is_dir_existed(origin_md_dir)
    is_dir_existed(local_md_dir, is_recreate=True)
    is_dir_existed(local_doc_dir, is_recreate=True)
    is_dir_existed(server_md_dir, is_recreate=True)
    loop = asyncio.get_event_loop()
    retrieve_md(origin_md_dir)
