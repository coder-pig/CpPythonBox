# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : wash_flutter_widgets.py
   Author   : CoderPig
   date     : 2023-12-28 10:42
   Desc     : 
-------------------------------------------------
"""
import os.path

import unicodedata

from util.file_util import read_file_text_content, write_text_to_file


# 输出属性介绍
def print_filed_format(origin_str):
    after_str = ""
    lines = origin_str.split('\n')
    for index, line in enumerate(lines):
        if len(line) > 0:
            temp_line = line.replace(" (非必须)", "").replace("。", "")
            if temp_line.startswith("key "):
                after_str += "- **key**：Key，**控制widget在树中的唯一性**；\n"
            else:
                field_name_split_list = temp_line.split("：")
                desc_split_list = field_name_split_list[1].split("，")
                after_str += "- **{}**：{}，**{}**{}；\n".format(field_name_split_list[0], desc_split_list[0],
                                                              desc_split_list[1],
                                                              "，" + desc_split_list[2] if (
                                                                      len(desc_split_list) > 2) else "")

    write_text_to_file(after_str[:-1], os.path.join(os.getcwd(), 'out.txt'))
    print(after_str)


# 输出代码示例
def print_demo(origin_str):
    after_str = ""
    catching_code = False
    lines = origin_str.split('\n')
    for index, line in enumerate(lines):
        if len(line) == 0:
            if catching_code:
                after_str += "\n```\n"
                catching_code = False
            else:
                after_str += "\n"
        else:
            if is_chinese_char(line[0]):
                if catching_code:
                    after_str += "```\n"
                    catching_code = False
                after_str += "\n### {}\n".format(line.replace("：", ""))
            else:
                if catching_code:
                    after_str += "{}\n".format(line)
                else:
                    after_str += "```\n{}\n".format(line)
                    catching_code = True
    write_text_to_file(after_str, os.path.join(os.getcwd(), 'out.txt'))
    print(after_str)


def is_chinese_char(ch):
    """判断一个字符是不是中文字符。"""
    return unicodedata.category(ch).startswith('Lo')


if __name__ == '__main__':
    content = read_file_text_content(os.path.join(os.getcwd(), 'in.txt'))
    print_filed_format(content)
    # print_demo(content)
