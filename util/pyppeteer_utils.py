# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : pyppeteer_utils.py
   Author   : CoderPig
   date     : 2023-02-23 17:35 
   Desc     : pyppeteer 工具类
-------------------------------------------------
"""
import asyncio
import time
import tkinter

from pyppeteer import launch


class PyBrowser:
    def __init__(self):
        self.url = None
        self.ua = ""

    # 获取屏幕大小
    def screen_size(self):
        tk = tkinter.Tk()
        width = tk.winfo_screenwidth()
        height = tk.winfo_screenheight()
        tk.quit()
        return width, height

    async def get_browser(self, headless=False):
        launch_args = [
            # "--proxy-server=http://127.0.0.1:8008",  # 设置浏览器代理
            "--no-sandbox",  # 非沙盒模式
            "--disable-infobars",  # 隐藏信息栏
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/83.0.4103.97 Safari/537.36 ",
            "--log-level=3",  # 日志等级，
        ]
        print("开始构造浏览器...")
        self.browser = await launch(
            {'headless': headless, 'args': launch_args, 'userDataDir': './userData', 'dumpio': True})
        self.page = await self.browser.newPage()
        width, height = self.screen_size()
        # 设置浏览器宽高
        await self.page.setViewport({
            'width': width, 'height': height
        })
        # 是否启用JS
        await self.page.setJavaScriptEnabled(True)
        await self.prevent_web_driver_check(self.page)
        print("浏览器初始化完毕...")

    # 获取当前操作页面
    async def cur_page(self):
        return self.page

    # 获取页面的url
    async def cur_page_url(self, page=None):
        if page is None:
            page = self.page
        return self.page.url

    # 打开一个新的页面
    async def get_new_page(self):
        return await self.browser.newPage()

    # 刷新当前页面
    async def reload(self):
        await self.page.reload()

    # 打开链接
    async def open(self, url, timeout=60):
        if url is None:
            print("传入url不能为空！")
            return None
        self.url = url
        print("打开网页：", url)
        self.res = await self.page.goto(url, options={'timeout': int(timeout * 1000)})
        await asyncio.sleep(3)  # 强行等待3s
        status = self.res.status
        cur_url = self.page.url
        await self.prevent_web_driver_check(self.page)
        return status, cur_url

    # 关闭当前打开的浏览器
    async def close_browser(self, browser):
        if browser is None:
            browser = self.browser
        try:
            await browser.close()
        except:
            pass

    # 关闭当前打开浏览器中的一个页面
    async def close_page(self, page):
        if page is None:
            page = self.page
        await page.close()

    # 关闭当前打开浏览器第几个页面
    async def close_page_by_num(self, number):
        if number is None:
            return None
        pages = await self.browser.pages()
        await pages[number].close()
        return True

    # 获取当前页面打开页面的响应状态
    async def resp_status(self):
        try:
            return self.res.status
        except:
            return 200

    # 截图
    async def screenshot(self, page, full=False):
        if page is None:
            page = self.page
        await page.screenshot(
            {'path': './screenshots/' + str(int(time.time() * 1000)) + '.png', 'quality': 100, 'fullPage': full})

    # 获取网页源码
    async def html(self, page):
        if page is None:
            page = self.page
        return await page.content()

    # 获取标题
    async def title(self, page):
        if page is None:
            page = self.page
        return await page.title()

    # 获取元素内容；                        ---OK---
    async def get_element_text(self, page, element):
        if element is None:
            print("当前传入的【element】不能为空，参数错误！！")
            return None
        if page is None:
            page = self.page
        if str(type(element)) == "<class 'list'>":
            print("当前传入的【element】不是单个对象，为list集合，参数错误！！")
            return None
        return await page.evaluate('(element) => element.textContent', element)

    # 通过选择器获取元素内容
    async def get_element_by_selector(self, page, selector):
        if selector is None:
            print("当前传入的【selector】不能为空，参数错误！！")
            return None
        if page is None:
            page = self.page
        return await page.querySelector(selector)

    # 滚动到页面底部
    async def scroll_to_bottom(self, page):
        if page is None:
            page = self.page
        await page.evaluate('window.scrollBy(0, document.body.scrollHeight)')

    # 防止WebDriver检测
    async def prevent_web_driver_check(self, page):
        if page is not None:
            await page.evaluate(
                '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => undefined } }) }''')
            # 以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果。
            await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
            await page.evaluate(
                '''() =>{ Object.defineProperty(navigator, 'lang uages', { get: () => ['en-US', 'en'] }); }''')
            await page.evaluate(
                '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
