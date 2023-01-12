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


def request_download_video(url, headers, video_path, file_type, title=''):
    logger.info("下载：%s" % url)
    file_name = '{}{}{}_{}.{}'.format(video_path, os.path.sep, title, str(int(round(time.time() * 1000))),
                                      file_type)
    resp = r.get(url=url, headers=headers)
    with open(file_name, "wb+") as f:
        f.write(resp.content)
        logger.info("下载完成：%s" % resp.url)
    return file_name


# you-get下载视频
def you_get_download_video(video_url, output_dir, cookie_file=None):
    if cookie_file is not None and os.path.exists(cookie_file):
        you_get.load_cookies(cookie_file)
    you_get.any_download(url=video_url, info_only=False, output_dir=output_dir, merge=True)


# IDM下载文件
def download_idm(url, referer_url, output_dir, file_type, title=''):
    logger.info("下载：%s" % url)
    file_name = '{}_{}.{}'.format(title, str(int(round(time.time() * 1000))), file_type)
    downloader = IDMan()
    downloader.download(url, path_to_save=output_dir, output=file_name, referrer=referer_url)
    logger.info("下载完成：%s" % url)
    return os.path.join(output_dir, file_name)
