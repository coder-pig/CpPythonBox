# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : generate_widget_object_by_xml.py
   Author   : CoderPig
   date     : 2023-07-12 17:52
   Desc     : 根据xml布局，生成Kotlin中可以直接调用的控件对象 (需要支持DataBinding)
-------------------------------------------------
"""
import re

from util.file_util import if_file_existed, read_file_text_content, write_text_to_file

weight_id_pattern = re.compile(r'\+id/([a-z0-9_]+)"(.*?(text|title)="(.*?)")?', re.S)  # 提取id和

origin_xml_file = "布局XML源文件.txt"
generate_kotlin_file = "生成的Kotlin控件代码.txt"

if __name__ == '__main__':
    if not if_file_existed(origin_xml_file):
        open(origin_xml_file, "w").close()
    xml_content = read_file_text_content(origin_xml_file)
    results = weight_id_pattern.findall(xml_content)
    if len(results) == 0:
        exit("布局XML源文件解析异常，请检查后重试...")
    else:
        kotlin_code_result = "mBinding.apply {\n"
        for result in results:
            id_split_list = result[0].split("_")
            weight_name = "\t" + id_split_list[0]
            for id_split in id_split_list[1:]:
                weight_name += id_split.capitalize()
            weight_name += ".apply {%s\n\n\t}\n" % ("" if (len(result[3]) == 0) else " //" + result[3])
            kotlin_code_result += weight_name
        kotlin_code_result += "}"
        write_text_to_file(kotlin_code_result, generate_kotlin_file)
