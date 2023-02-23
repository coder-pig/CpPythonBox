# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : boss.py
   Author   : CoderPig
   date     : 2023-02-23 11:04 
   Desc     : Boss直聘岗位数据爬取(自动化)
-------------------------------------------------
"""
from util.adb_util import current_ui_xml, analysis_ui_xml, swipe, sleep, print_node
from util.file_util import get_temp_save_root_path, is_dir_existed, write_text_to_file
from util.logger_util import default_logger
import os

result_file = "result.txt"
logger = default_logger()
temp_dir = get_temp_save_root_path()
remove_duplicates_set = set()
id_prefix = "com.hpbr.bosszhipin:id/{}"  # 资源id前缀


def crawl_data():
    while True:
        nodes = analysis_ui_xml(current_ui_xml(temp_dir))
        list_node = nodes.find_node_by_resource_id(id_prefix.format("recyclerView_list"))
        for vg_node in list_node.nodes:
            if len(vg_node.nodes) > 10:
                tv_position_name = vg_node.find_node_by_resource_id(id_prefix.format("tv_position_name"))
                if tv_position_name:
                    content = ""
                    for pos, node in enumerate(vg_node.nodes):
                        content += node.text
                        if pos < len(vg_node.nodes) - 1:
                            content += "|"
                    # 去重
                    split_list = content.split("|")
                    duplicate_key = split_list[0] + split_list[1]
                    if duplicate_key not in remove_duplicates_set:
                        write_text_to_file(content, result_file, "a+")
                        remove_duplicates_set.add(duplicate_key)
            else:
                logger.info("数据不完整，跳过")
        swipe(615, 1900, 625, 1750, 100)


if __name__ == '__main__':
    is_dir_existed(temp_dir, is_recreate=True)
    crawl_data()
