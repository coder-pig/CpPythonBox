# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : ocr_util.py
   Author   : CoderPig
   date     : 2022-12-23 14:53 
   Desc     : OCR文字识别工具类
-------------------------------------------------
"""

import socket
import requests as r
from collections import OrderedDict
from aip import AipOcr

from util.file_util import read_file_text_content, read_file_content

local_ocr_base_url = "http://{}:8089".format(socket.gethostbyname(socket.gethostname()))
local_ocr_tr_run_url = local_ocr_base_url + "/api/tr-run/"


def picture_local_ocr(pic_path):
    upload_files = {'file': open(pic_path, 'rb'), 'compress': 960}
    resp = r.post(local_ocr_tr_run_url, files=upload_files)
    return extract_text(resp.json())


def extract_text(origin_data_dict):
    text_dict = OrderedDict()
    raw_out = origin_data_dict['data']['raw_out']
    if raw_out is not None:
        for raw in raw_out:
            text_dict[raw[1]] = (raw[0][0][0], raw[0][0][1], raw[0][1][0], raw[0][2][1])
        return text_dict
    else:
        print("Json数据解析异常")


class BaiDuOCR:
    def __init__(self):
        self.APP_ID = "xxx"
        self.API_KEY = "xxx"
        self.SECRET_KEY = "xxx"
        self.client = AipOcr(self.APP_ID, self.API_KEY, self.SECRET_KEY)

    def general(self, pic_path):
        orc_result = self.client.basicGeneral(read_file_content(pic_path))
        if orc_result is not None:
            print("识别结果：" + str(orc_result))
            # 直接拿，就不判断了，反正识别错误就抛出异常
            return orc_result["words_result"][0]['words']
        else:
            print("识别失败")
            raise Exception("识别失败异常")


if __name__ == '__main__':
    ocr = BaiDuOCR()
    ocr.general("c2.jpg")
