# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : mall_spider.py
   Author   : CoderPig
   date     : 2023-06-13 17:06
   Desc     : 某小站点的爬取示例
-------------------------------------------------
"""
import datetime
import json
import os.path
import random
import time

import requests as r
import xlwt

from util.download_util import download_pic
from util.file_util import read_list_from_file, is_dir_existed, write_text_to_file, write_text_list_to_file, \
    search_all_file, read_file_text_content, copy_file

post_url = "http://xxx.xxx.xxx/dcpService/DCP/services/invoke"
output_dir = os.path.join(os.getcwd(), "output")
json_output_dir = os.path.join(output_dir, "json")
pic_output_dir = os.path.join(json_output_dir, "pic")
pic_zip_dir = os.path.join(json_output_dir, "zip")
temp_spider_category_list = []

default_headers = {
    'Host': 'xxx.xxx.xxx',
    'Origin': 'http://xxx.xx.xxx',
    'Referer': 'http://xxx.xxx.xxx',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/85.0.4183.121 Safari/537.36 ',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
}


def get_timestamp():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]


def login_fetch_token():
    login_data = {
        "serviceId": "DCP_LoginRetail",
        "request": {
            "eId": "10",
            "opNo": "82197",
            "loginType": "2",
            "password": "abb9865d4ada922b5f911c3c78caf273",
            "langType": "zh_CN"
        },
        "timestamp": get_timestamp(),
        "langType": "zh_CN",
        "plantType": "retailStore",
        "version": "3.3.0.3-2023-03-24"
    }
    resp = r.post(post_url, headers=default_headers, json=login_data)
    return resp.json()['token']


def fetch_good_list(category_record):
    global temp_spider_category_list
    category_split_list = category_record.split('-')
    category_id = category_split_list[5]
    fetch_list_data = {
        "serviceId": "DCP_GoodsFeatureQuery",
        "request": {
            "status": "100",
            "category": [category_id],
            "billType": "0",
            "ISHTTPS": "1",
            "DomainName": "xxx.xxx.xxx",
            "CheckSuppGoods": "N"
        },
        "pageNumber": 1,
        "pageSize": 30,
        "token": token,
        "timestamp": get_timestamp(),
        "langType": "zh_CN",
        "plantType": "retailStore",
        "version": "3.3.0.3-2023-03-24"
    }
    page = 1
    # 循环直到列表没数据
    while True:
        fetch_list_data['pageNumber'] = page
        list_data_resp = r.post(post_url, headers=default_headers, json=fetch_list_data)
        print("拉取" + category_record + "【第" + str(page) + "页】")
        plu_list = list_data_resp.json()['datas']['pluList']
        if len(plu_list) == 0:
            print(category_record + "没数据啦，拉下去一个类别...")
            temp_spider_category_list.append(category_record)
            write_text_list_to_file(temp_spider_category_list, "temp_spider_category.txt")
            break
        else:
            page += 1  # 拉取成功页数要+1
            plu_dict = {}  # 商品字典，键是商品序号，值是对应json字典，后面要把库存塞里面
            for plu in plu_list:
                plu_dict[plu['pluNo']] = plu
            plu_no_list = []
            for plu_no in plu_dict.keys():
                plu_no_list.append({"pluNo": plu_no})
            # 请求商品库存
            fetch_qty_data = {
                "serviceId": "DCP_GoodsStockQuery_Open",
                "request": {
                    "eId": "10",
                    "queryDate": "",
                    "queryType": "ERP",
                    "warehouse": "",
                    "stockQtyType": "",
                    "pluList": plu_no_list
                },
                "timestamp": get_timestamp(),
                "token": token,
                "langType": "zh_CN",
                "plantType": "retailStore",
                "version": "3.3.0.3-2023-03-24"
            }
            qty_data_resp = r.post(post_url, headers=default_headers, json=fetch_qty_data)
            print("拉取当前列表的商品库存")
            for qty_data in qty_data_resp.json()['datas']['pluList']:
                plu_dict[qty_data['pluNo']]['baseQty'] = qty_data['baseQty']
            # 保存商品对应的json数据文件到本地
            plu_data_list = list(plu_dict.values())
            for plu_data in plu_data_list:
                save_dir = os.path.join(json_output_dir,
                                        category_split_list[0].replace("/", ",").replace("*", "x") + os.path.sep
                                        + category_split_list[1].replace("/", ",").replace("*", "x") + os.path.sep
                                        + category_split_list[2].replace("/", ",").replace("*", "x") + os.path.sep
                                        + category_split_list[3].replace("/", ",").replace("*", "x") + os.path.sep
                                        + category_split_list[4].replace("/", ",").replace("*", "x") + os.path.sep)
                is_dir_existed(save_dir)
                write_text_to_file(json.dumps(plu_data, ensure_ascii=False),
                                   os.path.join(save_dir, plu_data['pluNo'] + ".json"))
        time.sleep(random.randint(5, 10))


# 批量下载图片到本地

async def download_pics():
    json_file_list = search_all_file(json_output_dir, (".json",))
    for json_file in json_file_list:
        good_json = json.loads(read_file_text_content(json_file))
        pic_url = good_json['listImage']
        if pic_url is not None and len(pic_url) != 0:
            await download_pic(os.path.join(pic_output_dir, os.path.basename(pic_url)), pic_url)


# 生成Excel
def generate_excel():
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet("商品列表")
    header_list = ["商品条码", "商品名称", "类别", "规格", "尺寸", "件装数", "进货价", "零售价", "供应商"]
    # 写入表头
    for pos, header in enumerate(header_list):
        worksheet.write(0, pos, label=header)
    # 写入表数据
    json_file_list = search_all_file(json_output_dir, (".json",))
    # 行计数器
    count = 1
    for json_file in json_file_list:
        good_json = json.loads(read_file_text_content(json_file))
        category_str = ""
        for category in json_file.replace(os.getcwd(), "").split(os.path.sep)[1: -1]:
            category_str += category + "-"
        worksheet.write(count, 0, good_json['pluNo'])
        worksheet.write(count, 1, good_json['pluName'])
        worksheet.write(count, 2, category_str[:-1])
        worksheet.write(count, 3, good_json['unitRatio'] + good_json['unitName'])
        size_str = good_json['len'] + "x" + good_json['width'] + "x" + good_json['height'] + good_json['volumeUnitName']
        if size_str == "xx" or size_str == "0x0x0":
            size_str = ""
        worksheet.write(count, 4, size_str)
        worksheet.write(count, 5, good_json['maxOrderSpec'])
        worksheet.write(count, 6, good_json['distriPrice'])
        worksheet.write(count, 7, good_json['standardPrice'])
        worksheet.write(count, 8, good_json['mainSupplierName'] + "-" + good_json['mainSupplierAbbr'])
        # 图片做下处理
        pic_url = good_json['listImage']
        if pic_url is not None and len(pic_url) > 0:
            pic_file_name = os.path.basename(pic_url)
            for pic_file in pic_file_list:
                if pic_file_name in pic_file:
                    print("复制文件：", pic_file)
                    copy_file(pic_file,
                              os.path.join(pic_zip_dir, good_json['pluNo'] + "." + pic_file_name.split(".")[-1]))
        count += 1
    workbook.save("店铺商品数据_{}.xls".format(int(time.time())))


if __name__ == '__main__':
    is_dir_existed(output_dir)
    is_dir_existed(json_output_dir)
    is_dir_existed(pic_output_dir)
    is_dir_existed(pic_zip_dir)

    # 打印出Token
    # print(login_fetch_token())

    # 读取已爬取的商品类别
    # temp_spider_category_list = read_list_from_file("temp_spider_category.txt")

    # 读取遍历商品分类列表
    category_list = read_list_from_file("category_record.txt")
    # for category in category_list:
    #     fetch_good_list(category)

    # 批量下载图片
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(download_pics())

    # 生成excel表哥
    pic_file_list = search_all_file(pic_output_dir, (".jpg", ".jpeg", ".png", ".JPG", ".jPG", "PNG"))
    # generate_excel()
