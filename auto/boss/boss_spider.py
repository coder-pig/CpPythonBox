# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : boss_spider.py
   Author   : CoderPig
   date     : 2023-02-23 17:33 
   Desc     : boss直聘爬虫
-------------------------------------------------
"""
import asyncio
import time

from util.logger_util import default_logger
from util.pyppeteer_utils import PyBrowser

logger = default_logger()


async def login():
    browser = PyBrowser()
    await browser.get_browser()
    await browser.open("https://www.zhipin.com/web/user/?ka=header-login")
    await browser.page.waitForSelector('.wx-login-btn')
    await browser.page.click('.wx-login-btn')
    await browser.page.type('.wx-login-btn')
    logger.info("等待扫码, 10s后自动关闭")
    await asyncio.sleep(10)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(login())
