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
from collections import OrderedDict
import requests as r
from aip import AipOcr
from urllib3.exceptions import NewConnectionError

from config_getter import get_config
from util.file_util import read_file_content
from util.logger_util import default_logger

logger = default_logger()

# 本地OCR相关
local_ocr_base_url = "http://{}:8089".format(socket.gethostbyname(socket.gethostname()))
local_ocr_tr_run_url = local_ocr_base_url + "/api/tr-run/"

# 百度OCR相关
bd_ocr_client = AipOcr(get_config("bd_ocr_app_id"), get_config("bd_ocr_api_key"), get_config("bd_ocr_secret_key"))


def picture_local_ocr(pic_path):
    """
    图片本地OCR
    :param pic_path: 待识别图片路径
    :return: 识别结果，返回字典(文字：文字区域)
    """
    upload_files = {'file': open(pic_path, 'rb'), 'compress': 960}
    try:
        resp = r.post(local_ocr_tr_run_url, files=upload_files)
        return extract_text(resp.json())
    except (NewConnectionError, r.exceptions.ConnectionError):
        logger.error("连接本地OCR服务异常，请检测本地服务是否启动？")


def extract_text(origin_data_dict):
    """
    解析识别结果的方法
    :param origin_data_dict: 本地OCR识别结果
    :return:
    """
    text_dict = OrderedDict()
    raw_out = origin_data_dict['data']['raw_out']
    if raw_out is not None:
        for raw in raw_out:
            text_dict[raw[1]] = (raw[0][0][0], raw[0][0][1], raw[0][1][0], raw[0][2][1])
        return text_dict
    else:
        logger.info("Json数据解析异常")


def bd_ocr_general(pic_path):
    """
    百度OCR识别
    :param pic_path:
    :return:
    """
    orc_result = bd_ocr_client.basicGeneral(read_file_content(pic_path))
    if orc_result is not None:
        logger.info("识别结果：{}".format(orc_result))
        # 直接拿，就不判断了，反正识别错误就抛出异常
        return orc_result["words_result"][0]['words']
    else:
        logger.info("识别失败")
        raise Exception("识别失败异常")


if __name__ == '__main__':
    print(picture_local_ocr("c1.png"))
