# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : auto_to_list.py
   Author   : CoderPig
   date     : 2023-04-17 15:09
   Desc     : 
-------------------------------------------------
"""
import re

from util.file_util import read_file_text_content, write_text_to_file

first_pattern = re.compile(r" +\n", re.S)  # 空白行
second_pattern = re.compile(r"([0-9.]+\n)", re.S)  # 添加一级表头
third_pattern = re.compile(r"(^[^- ](.*?)\n)", re.M)  # 添加二级表头
forth_pattern = re.compile(r"(^)", re.M)  # 添加二级表头

if __name__ == '__main__':
    content = read_file_text_content("origin.md")
    content = first_pattern.sub("", content)
    # content = second_pattern.sub(r"- \g<1>", content)
    # content = third_pattern.sub(r" - \g<1>", content)
    content = forth_pattern.sub(r"- \g<1>", content)
    write_text_to_file(content.rstrip().replace("\u200B", ""), "result.md")
