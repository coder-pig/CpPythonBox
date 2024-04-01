# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : bd_poi_data_fetch.py
   Author   : CoderPig
   date     : 2024-02-23 15:35
   Desc     : 提取百度景点信息
-------------------------------------------------
"""
import json
import os
import csv

from util.file_util import read_file_text_content, search_all_file, write_text_to_file, write_text_list_to_file

output_dir = os.path.join(os.getcwd(), "output")


# 提取城市_区所有景点信息列表
def fetch_attractions_info_list(city_county):
    json_dir = "{}{}{}{}{}".format(os.getcwd(), os.sep, "baidu_jd", os.sep, city_county, os.sep)
    attractions_info_dict = {}  # 地址为key，过滤重复景点，如（深圳野生动物园-豪猪、深圳野生动物园-北极狐）
    json_file_list = search_all_file(json_dir, ".json")
    pos_count = 1
    result_str = ""
    for json_file in json_file_list:
        data_list = json.loads(read_file_text_content(json_file))['content']
        for data in data_list:
            attractions_name = data['name']  # 景点名称
            attractions_tag = data['std_tag']  # 景点标签
            attractions_addr = data['addr']  # 景点地址
            # 过滤垃圾数据
            if attractions_tag:
                if "景点" in attractions_tag or "公园" in attractions_tag:
                    # 景点记录
                    attractions_dict = {"景点序号": pos_count, "景点名称": attractions_name,
                                        "景点标签": attractions_tag,
                                        "景点地址": attractions_addr}
                    if attractions_addr in attractions_info_dict:
                        cur_attractions_name = attractions_info_dict[attractions_addr]['景点名称']
                        # 取景点名称较短的那一个
                        if len(attractions_name) < len(cur_attractions_name):
                            attractions_dict['景点序号'] = attractions_info_dict[attractions_addr]['景点序号']
                            attractions_info_dict[attractions_addr] = attractions_dict
                    else:
                        attractions_info_dict[attractions_addr] = attractions_dict
                        pos_count += 1

        # 保存为csv文件
        with open(os.path.join(output_dir, "{}.csv".format(city_county)), 'w+', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['景点序号', '景点名称', "景点标签", "景点地址"])
            writer.writeheader()
            for item in list(attractions_info_dict.values()):
                writer.writerow(item)
    for item in attractions_info_dict.values():
        result_str += "【{}】{}\n".format(item['景点名称'], item['景点地址'])
    write_text_to_file(result_str, os.path.join(output_dir, "{}.txt".format(city_county)))

if __name__ == '__main__':
    city_county_list = ['sz-ns', 'sz-ba', 'sz-ft', 'sz-lg', 'sz-lh', 'sz-luoh']
    fetch_attractions_info_list(city_county_list[0])
