# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : backups_util.py
   Author   : CoderPig
   date     : 2023-10-30 14:10
   Desc     : 备份工具类
-------------------------------------------------
"""
import os
import time
from functools import partial

import aiofiles
from aiohttp_requests import requests

from util.file_util import is_dir_existed, search_all_file, write_text_to_file, read_file_text_content
from util.logger_util import default_logger

logger = default_logger()
order_set = {i for i in range(1, 500000)}  # 避免图片名重复后缀
pic_url_path_record_list = []
default_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/85.0.4183.121 Safari/537.36 '
}


def md_to_local(input_dir=os.getcwd(), output_dir=os.getcwd(), pic_match_pattern=None, loop=None, pic_url_func=None,
                pic_suffix_func=None, replace_result_func=None):
    """
    ma文件本地化
    :param input_dir: 要本地化md文件的输入目录
    :param output_dir: 本地化后md文件的输出目录
    :param pic_match_pattern: 匹配图片url的正则
    :param loop: Asyncio event loop，用来执行图片下载任务
    :param pic_url_func:    生成图片URL的方法，从正则匹配结果里拿
    :param pic_suffix_func: 生成文件后缀的方法，从正则匹配结果里拿
    :param replace_result_func: 生成替换后的文本的方法
    """

    global pic_url_path_record_list
    pic_url_path_record_list = []
    origin_md_list = search_all_file(input_dir, "md")
    if len(origin_md_list) == 0:
        exit("未检测到md文件")
    else:
        for md_file_path in origin_md_list:
            # 读取md文件内容
            old_content = read_file_text_content(md_file_path)
            # 定位oring_md所在的下标，拼接新生成的md文件的目录要用到
            absolute_dir_index = md_file_path.find("origin_md")
            # 新md文件的相对路径
            md_relative_path = md_file_path[absolute_dir_index + 10:]
            # 新md文件所在目录
            new_md_dir = os.path.join(output_dir, md_relative_path[:-3])
            # 新md文件的完整路径
            new_md_file_path = os.path.join(new_md_dir, os.path.basename(md_file_path))
            # 图片的保存路径
            new_picture_dir = os.path.join(new_md_dir, "images")
            # 路径不存在新建
            is_dir_existed(new_md_dir)
            is_dir_existed(new_picture_dir)
            # 替换原内容
            new_content = pic_match_pattern.sub(
                partial(pic_to_local, pic_save_dir=new_picture_dir, pic_url_func=pic_url_func,
                        pic_suffix_func=pic_suffix_func, replace_result_func=replace_result_func), old_content)
            # 生成新的md文件
            write_text_to_file(new_content, new_md_file_path)
            logger.info("新md文件已生成 → {}".format(new_md_file_path))
        logger.info("所有本地md文件生成完毕！开始批量下载图片文件")
        for pic_url_path_record in pic_url_path_record_list:
            split_list = pic_url_path_record.split("\t")
            loop.run_until_complete(download_pic(split_list[1], split_list[0]))


# 远程图片转换为本地图片
def pic_to_local(match_result, pic_save_dir, pic_url_func=None, pic_suffix_func=None, replace_result_func=None):
    """
    图片链接本地化，替换原本的远程图片URL为本地相对路径，把图片URL加入到下载列表
    :param match_result: 正则匹配结果，可以通过下标获取不同分组的值
    :param pic_save_dir: 图片保存路径
    :param pic_url_func:  生成图片URL的方法，从正则匹配结果里拿
    :param pic_suffix_func:  生成图片后缀的方法，从正则匹配结果里拿
    :param replace_result_func: 生成替换后的文本的方法
    """

    global pic_url_path_record_list
    pic_url = pic_url_func(match_result)
    logger.info("替换前的图片路径：{}".format(pic_url))
    # 生成新的图片名
    img_file_name = "{}_{}.{}".format(int(round(time.time())), order_set.pop(), pic_suffix_func(match_result))
    # 拼接图片相对路径(Markdown用到的)
    relative_path = 'images/{}'.format(img_file_name)
    # 拼接图片绝对路径，下载到本地
    absolute_path = os.path.join(pic_save_dir, img_file_name)
    logger.info("替换后的图片路径：{}".format(relative_path))
    pic_url_path_record_list.append("{}\t{}".format(pic_url, absolute_path))
    # 拼接前后括号()
    return replace_result_func(match_result, relative_path)


async def download_pic(pic_path, url, headers=None):
    """
    协程异步卸载图片
    :param pic_path: 图片保存路径
    :param url: 图片URL
    :param headers: 下载请求头
    """

    try:
        if headers is None:
            headers = default_headers
        if url.startswith("http") | url.startswith("https"):
            if os.path.exists(pic_path):
                logger.info("图片已存在，跳过下载：%s" % pic_path)
            else:
                resp = await requests.get(url, headers=headers)
                logger.info("下载图片：%s" % resp.url)
                if resp is not None:
                    if resp.status != 404:
                        async with aiofiles.open(pic_path, "wb+") as f:
                            await f.write(await resp.read())
                            logger.info("图片下载完毕：%s" % pic_path)
                    else:
                        logger.info("图片不存在：{}".format(url))
        else:
            logger.info("图片链接格式不正确：%s - %s" % (pic_path, url))
    except Exception as e:
        logger.info("下载异常：{}\n{}".format(url, e))
