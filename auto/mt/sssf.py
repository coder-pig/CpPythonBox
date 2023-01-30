# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : sssf.py
   Author   : CoderPig
   date     : 2023-01-12 14:21 
   Desc     : 谁是首富自动做任务脚本
-------------------------------------------------
"""
import re

from util.adb_util import screenshot, click_area, sleep, click_xy, long_click_xy
from util.file_util import get_temp_save_root_path, is_dir_existed
from util.logger_util import default_logger
from util.ocr_util import picture_local_ocr
from util.pic_util import *

logger = default_logger()
temp_dir = get_temp_save_root_path()
pk_count_pattern = re.compile(r'次数.*?(\d+)')  # 获取挑战次数的正则
number_pattern = re.compile(r'能力.*?(\d+\.\d)')  # 获取战力的正则


# 自动PK
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
                if min_value > power_value:
                    min_value = power_value
                    min_value_area = ocr_result_dict[ocr_result]
        if start_area:
            logger.info("执行第{}次PK".format(pk_count))
            if min_value_area:
                logger.info("选中战力：{}万".format(min_value))
                click_area(*min_value_area)
                sleep(0.1)
                click_area(*start_area)
                sleep(0.1)
                click_xy(469, 1849)
                # 开会员
                sleep(0.1)
                click_xy(938, 1768)
                # 没开会员
                # sleep(15)
                click_xy(469, 1849)
                sleep(0.1)
                continue
            else:
                logger.info("未检索到最低战力值")
        else:
            logger.info("未检索到开始按钮，可能PK还没结束，休眠5s")
            sleep(5)
            continue


# 求卷积
def convolution(img, x, y):
    convolution_list = [1, 1, 1, 1, -8, 1, 1, 1, 1]  # 卷积核列表
    color_list = []
    xl = [x - 1, x, x + 1]
    yl = [y - 1, y, y + 1]
    for j in yl:
        for i in xl:
            color = img.getpixel((i, j))  # 取出色值
            color_list.append(color)
    c = 0
    for i, j in zip(convolution_list, color_list):
        c = c + i * j
    return c


# 边缘检测
def edge_detection(origin_pic):
    origin_img = Image.open(origin_pic)
    w, h = origin_img.size
    new_img = Image.new('L', (w, h), "white")
    border_x_set = set()  # 存储x坐标的集合
    for x in range(1, w - 1):
        for y in range(1, h - 1):
            c = convolution(origin_img, x, y)
            if c > 0:
                s = 0
            else:
                s = 255
            new_img.putpixel((x, y), s)
            if s == 0:
                border_x_set.add(x)
    border_x_list = list(border_x_set)
    border_x_list.sort()  # 升序
    border_x_list_len = len(border_x_list)
    point_x_list = [border_x_list[0]]  # 存储x坐标，第一个点肯定是左边缘
    for pos in range(1, border_x_list_len):
        # 前后两个点间距超过10像素
        if border_x_list[pos] - border_x_list[pos - 1] > 50:
            point_x_list.append(border_x_list[pos - 1])
            point_x_list.append(border_x_list[pos])
    point_x_list.append(border_x_list[border_x_list_len - 1])  # 最后一个点肯定是右边缘
    print(point_x_list)
    first_center_x = int((point_x_list[0] + point_x_list[1]) / 2)
    second_center_x = int((point_x_list[2] + point_x_list[3]) / 2)
    distance = second_center_x - first_center_x
    print("第一个数字的中心x坐标为：{}，第二个数字的中心x坐标为：{}，得出木板的长度应为：{}".format(first_center_x, second_center_x, distance))
    return distance


# 无脑遍历坐标点
def traverse_points(origin_pic):
    origin_img = Image.open(origin_pic)
    w, h = origin_img.size
    first_start_x = -1  # 第一个数字的左边坐标
    second_end_x = -1  # 第二个数字的右边坐标
    start_x = 0
    end_x = w - 1
    while True:
        if first_start_x != -1 and second_end_x != -1:
            break
        if start_x < end_x:
            if first_start_x == -1:
                for y in range(h):
                    if origin_img.getpixel((start_x, y)) == 255:
                        first_start_x = start_x
                        break
                start_x += 1
            if second_end_x == -1:
                for y in range(h):
                    if origin_img.getpixel((end_x, y)) == 255:
                        second_end_x = end_x
                        break
                end_x -= 1
        else:
            exit("未发现目标坐标点")
            break
    center_x = int((first_start_x + second_end_x) / 2)
    first_end_x = -1
    second_start_x = -1
    for x in range(center_x, first_end_x, -1):
        if first_end_x == -1:
            for y in range(h):
                if origin_img.getpixel((x, y)) == 255:
                    first_end_x = x
                    break
        else:
            break
    for x in range(center_x, second_end_x):
        if second_start_x == -1:
            for y in range(h):
                if origin_img.getpixel((x, y)) == 255:
                    second_start_x = x
                    break
        else:
            break
    first_center_x = int((first_start_x + first_end_x) / 2)
    second_center_x = int((second_start_x + second_end_x) / 2)
    distance = second_center_x - first_center_x
    logger.info("{},{},{},{}".format(first_start_x, first_end_x, second_start_x, second_end_x))
    logger.info("第一个数字的中心x坐标为：{}，第二个数字的中心x坐标为：{}，得出木板的长度应为：{}".format(first_center_x, second_center_x, distance))
    return distance


# 孤岛求生自动跳桥
def auto_bridge():
    # 裁剪出数字那一排
    crop_pic = crop_area(screenshot(temp_dir), temp_dir, 0, 1262, 1080, 1336)
    # 灰度二值化
    bw_pic = picture_to_black_white(crop_pic, temp_dir, 240)
    # 卷积运算检测文字边缘
    # distance = edge_detection(bw_pic)
    # 无脑遍历坐标点
    distance = traverse_points(bw_pic) - 50
    duration = int(float(distance / 88.5) * 100)
    logger.info("两者间距：{}，长按{}ms".format(distance, duration))
    long_click_xy(546, 1774, duration)


def auto_bridge_old():
    bw_img = Image.open(
        picture_to_black_white(crop_area(screenshot(temp_dir), temp_dir, 0, 1262, 1080, 1336), temp_dir, 240))
    w, h = bw_img.size
    start_x = -1
    end_x = -1
    top_y = -1
    bottom_y = -1
    for x in range(w):
        for y in range(h):
            if bw_img.getpixel((x, y)) == 255:
                if start_x == -1 or start_x > x:
                    start_x = x
                if end_x == -1 or start_x < x:
                    end_x = x
                if top_y == -1 or top_y > y:
                    top_y = y
                if bottom_y == -1 or bottom_y < y:
                    bottom_y = y
    first_end_x = -1
    second_start_x = -1
    center_x = int((start_x + end_x) / 2)
    for x in range(center_x, start_x, -1):
        if first_end_x != -1:
            break
        for y in range(top_y, bottom_y):
            if bw_img.getpixel((x, y)) == 255:
                first_end_x = x
                break
    for x in range(center_x, end_x):
        if second_start_x != -1:
            break
        for y in range(top_y, bottom_y):
            if bw_img.getpixel((x, y)) == 255:
                second_start_x = x
                break
    first_center_x = int((start_x + first_end_x) / 2)
    second_center_x = int((second_start_x + end_x) / 2)
    # 求出距离
    distance = second_center_x - first_center_x - 70
    duration = int(float(distance / 86) * 100)
    print("两者间距：{}，长按{}ms".format(distance, duration))
    # 速度 7px/10ms   → 72px/100ms
    long_click_xy(546, 1774, duration)


# 春节自动答题(对联)
def auto_spring_answer():
    answer_dict = {
        "一": "四季财原顺意来、万事如意福临门", "四": "八节永平安", "山": "水清百鸟争春", "人": "思发在花前", "合": "内外平安好运来", "家": "春浓日暖花香",
        "新": "佳年顺景财源来", "卯": "兔岁报新春", "爆": "春风送暖入屠苏、桃符万户更新", "时": "好花应时而开", "春": "岁月赋诗情、花信早传梅", "青": "绿水溢春华",
        "绿": "红梅正报万家春"
    }
    print(picture_local_ocr(crop_area("c1.jpg", temp_dir, 50, 497, 201, 620)))

    # ocr = BaiDuOCR()
    # while True:
    #     input()
    #     orc_result = ocr.general(crop_area(screenshot(temp_dir), temp_dir, 44, 497, 194, 1403))
    #     webbrowser.open("https://www.baidu.com/s?wd={}下一句".format(orc_result))
    # crop_area("c2.jpg", temp_dir, 886, 505, 1032, 1396)
    # crop_area("c2.jpg", temp_dir, 78, 1750, 1027, 2022)


if __name__ == '__main__':
    is_dir_existed(temp_dir, is_recreate=True)
    for i in range(0, 60):
        auto_bridge_old()
        time.sleep(3)
    # auto_pk()
    # auto_spring_answer()
