# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : sssf.py
   Author   : CoderPig
   date     : 2023-01-12 14:21 
   Desc     : 谁是首富
-------------------------------------------------
"""
import re

from util.adb_util import screenshot, click_area, sleep, click_xy
from util.file_util import get_temp_save_root_path
from util.logger_util import default_logger
from util.ocr_util import picture_local_ocr

logger = default_logger()
temp_dir = get_temp_save_root_path()
pk_count_pattern = re.compile(r'次数.*?(\d+)')  # 获取挑战次数的正则
number_pattern = re.compile(r'能力.*?(\d+\.\d)')  # 获取战力的正则


def auto_pk():
    while True:
        ocr_result_dict = picture_local_ocr(screenshot(temp_dir))
        pk_count = 0  # 剩余挑战次数
        min_value = 100000  # 最低战力
        min_value_area = None  # 最小战力点击区域
        start_area = None  # 开始按钮
        for ocr_result in ocr_result_dict.keys():
            if "开始" in ocr_result:
                start_area = ocr_result_dict[ocr_result]
            # 筛挑战次数
            pk_count_result = pk_count_pattern.search(ocr_result)
            if pk_count_result:
                pk_count = int(pk_count_result.group(1))
                if pk_count == 0:
                    logger.info("挑战次数为0，执行结束")
                    break
            # 再筛最低战力
            number_result = number_pattern.search(ocr_result)
            if number_result:
                power_value = float(number_result.group(1))
                if power_value < min_value:
                    min_value = power_value
                    min_value_area = ocr_result_dict[ocr_result]
        if start_area:
            logger.info("执行第{}次PK".format(pk_count))
            if min_value_area:
                logger.info("选中战力：{}万".format(min_value))
                click_area(*min_value_area)
                sleep(1)
                click_area(*start_area)
                sleep(1)
                click_xy(469, 1849)
                sleep(10)
                click_xy(469, 1849)
                sleep(2)
                continue
            else:
                logger.info("未检索到最低战力值")
        else:
            logger.info("未检索到开始按钮，可能PK还没结束，休眠5s")
            sleep(5)
            continue


if __name__ == '__main__':
    auto_pk()
