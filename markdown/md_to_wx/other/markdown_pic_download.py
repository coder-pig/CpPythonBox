# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : markdown_pic_download.py
   Author   : CoderPig
   date     : 2023-01-11 18:06 
   Desc     : Markdownt图片批量下载
-------------------------------------------------
"""
import urllib.request
import time
import mistune
import os

from util.file_util import is_dir_existed, delete_file, read_file_text_content


class PicRenderer(mistune.HTMLRenderer):
    def image(self, src, alt="", title=None):
        pic_url_list.append(src)
        return ''


if __name__ == '__main__':
    md_file_path = os.path.join(os.getcwd(), "../article/md/test.md")
    pic_save_dir = os.path.join(os.getcwd(), "../article/pic/")
    delete_file(pic_save_dir)
    is_dir_existed(pic_save_dir)
    file_content = read_file_text_content(md_file_path)
    pic_url_list = []
    md_content = mistune.markdown(mistune.create_markdown(renderer=PicRenderer())(file_content))
    for pic_url in pic_url_list:
        print("下载：", pic_url)
        time.sleep(1)
        urllib.request.urlretrieve(pic_url,
                                   pic_save_dir + str(int(round(time.time() * 1000))) + '.' + pic_url.split('.')[-1])
