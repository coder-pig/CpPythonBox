# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : download_util.py
   Author   : CoderPig
   date     : 2023-01-06 16:59 
   Desc     : 下载工具类
-------------------------------------------------
"""

import os
import time

import aiofiles
import requests as r
from aiohttp_requests import requests
from idm import IDMan
from you_get import common as you_get

from util.logger_util import default_logger

logger = default_logger()

default_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/85.0.4183.121 Safari/537.36 '
}


async def download_pic(pic_path, url, headers=None):
    """
    异步下载图片的方法
    :param pic_path: 图片保存路径
    :param url: 图片URL
    :param headers: 请求头
    :return:
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


def request_download_file(url, headers, file_path, file_type, title=''):
    """
    requests库同步下载文件
    :param url: 文件URL
    :param headers: 请求头
    :param file_path: 文件路径
    :param file_type: 文件后缀
    :param title: 文件名
    :return:
    """
    logger.info("下载：%s" % url)
    file_name = '{}{}{}_{}.{}'.format(file_path, os.path.sep, title, str(int(round(time.time() * 1000))),
                                      file_type)
    resp = r.get(url=url, headers=headers)
    with open(file_name, "wb+") as f:
        f.write(resp.content)
        logger.info("下载完成：%s" % resp.url)
    return file_name


def you_get_download_video(video_url, output_dir, cookie_file=None):
    """
    you-get下载视屏
    :param video_url: 视频url
    :param output_dir: 保存目录
    :param cookie_file: Cookies文件
    :return:
    """
    if cookie_file is not None and os.path.exists(cookie_file):
        you_get.load_cookies(cookie_file)
    you_get.any_download(url=video_url, info_only=False, output_dir=output_dir, merge=True)


def download_idm(url, referer_url, output_dir, file_type, title=''):
    """
    IDM下载文件
    :param url: 文件URL
    :param referer_url: Refer请求头
    :param output_dir: 保存目录
    :param file_type:  文件后缀
    :param title: 文件名
    :return:
    """
    logger.info("下载：%s" % url)
    file_name = '{}_{}.{}'.format(title, str(int(round(time.time() * 1000))), file_type)
    downloader = IDMan()
    downloader.download(url, path_to_save=output_dir, output=file_name, referrer=referer_url)
    logger.info("下载完成：%s" % url)
    return os.path.join(output_dir, file_name)
