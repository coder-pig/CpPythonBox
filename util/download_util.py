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
from aiohttp_requests import requests
import aiofiles
import os

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
