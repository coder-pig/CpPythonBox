# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : generate_category_file.py
   Author   : CoderPig
   date     : 2023-06-13 16:42
   Desc     : 
-------------------------------------------------
"""
import json

from util.file_util import read_file_text_content, write_text_list_to_file

if __name__ == '__main__':
    category_list = []
    category_json = json.loads(read_file_text_content("category.json"))
    for data in category_json['datas']['category']:
        root_category_name = data['categoryName'] + "-"
        for first_child in data['child']:
            first_category_str = first_child['categoryName'] + "-"
            for second_child in first_child['child']:
                second_category_str = second_child['categoryName'] + "-"
                for third_child in second_child['child']:
                    third_category_str = third_child['categoryName'] + "-"
                    for forth_child in third_child['child']:
                        forth_category_str = forth_child['categoryName'] + "-" + forth_child['category']
                        category_list.append(
                            root_category_name + first_category_str + second_category_str + third_category_str + forth_category_str)

    write_text_list_to_file(category_list, "category_record.txt")
