# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : app.py
   Author   : CoderPig
   date     : 2023-04-13 11:24
   Desc     : 修正url风格，如：![][1] → ![](xxx)
-------------------------------------------------
"""
import re

from util.file_util import read_file_text_content, write_text_to_file

url_prefix_pattern = re.compile(r"\[.*?]\[\d+]", re.M)
url_suffix_pattern = re.compile(r"\[.*?]: http.*", re.M)

if __name__ == '__main__':
    content = read_file_text_content("origin.md")
    prefix_result = url_prefix_pattern.findall(content)
    suffix_result = url_suffix_pattern.findall(content)
    for pos in range(len(prefix_result)):
        prefix_end_pos = prefix_result[pos].rfind("[")
        prefix_str = prefix_result[pos][:prefix_end_pos]
        suffix_start_pos = suffix_result[pos].find(":")
        suffix_str = suffix_result[pos][suffix_start_pos + 2:]
        content = content.replace(suffix_result[pos], "")
        content = content.replace(prefix_result[pos], "%s(%s)" % (prefix_str, suffix_str))
    write_text_to_file(content.rstrip(), "result.md")

