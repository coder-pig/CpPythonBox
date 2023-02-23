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

from pyppeteer import launch

from util.adb_util import screenshot, click_area, sleep, click_xy, long_click_xy
from util.file_util import get_temp_save_root_path, is_dir_existed
from util.logger_util import default_logger
from util.ocr_util import picture_local_ocr
from util.pic_util import *

logger = default_logger()
temp_dir = get_temp_save_root_path()
pk_count_pattern = re.compile(r'次数.*?(\d+)')  # 获取挑战次数的正则
number_pattern = re.compile(r'能力.*?(\d+\.\d)([万亿]{1})')  # 获取战力的正则
chinese_pattern = re.compile(".*?([\u4e00-\u9fa5]+)", re.S)  # 筛选中文的正则


# 自动PK
def auto_pk():
    while True:
        ocr_result_dict = picture_local_ocr(screenshot(temp_dir))
        pk_count = 0  # 剩余挑战次数
        min_value = -1  # 最低战力
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
                unit = number_result.group(2)
                power_value = float(number_result.group(1)) * (10000 if unit == "亿" else 1)
                if min_value < power_value < 20000:
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
    logger.info(point_x_list)
    first_center_x = int((point_x_list[0] + point_x_list[1]) / 2)
    second_center_x = int((point_x_list[2] + point_x_list[3]) / 2)
    distance = second_center_x - first_center_x
    logger.info("第一个数字的中心x坐标为：{}，第二个数字的中心x坐标为：{}，得出木板的长度应为：{}".format(first_center_x, second_center_x, distance))
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


# 孤岛求生自动跳桥(旧)
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
    logger.info("两者间距：{}，长按{}ms".format(distance, duration))
    # 速度 7px/10ms   → 72px/100ms
    long_click_xy(546, 1774, duration)


# 自动全球交易
def auto_business():
    order_point = (888, 188)  # 订单红点
    merge_point = (459, 1843)  # 订单红点
    red_point_list = [(423, 748), (327, 1172), (775, 1333), (880, 889)]  # 碎片的小红点
    add_point_list = [(354, 806), (267, 1220), (714, 1397), (813, 947)]  # 碎片的加号
    # 战力值坐标
    power_area_list = [
        (284, 850, 363, 886), (560, 849, 639, 885), (840, 847, 915, 887),
        (284, 1208, 364, 1244), (570, 1202, 629, 1247), (840, 1206, 915, 1246)
    ]
    refresh_point = [326, 1548, 399, 1588]  # 刷新坐标
    challenge_point = [682, 1549, 752, 1586]  # 挑战坐标
    jump_point = [856, 1746, 952, 1798]  # 跳过
    while True:
        red_point_visible_list = [False, False, False, False]  # 检测是否有未收集的碎片
        cur_img = Image.open(screenshot(temp_dir))
        logger.info("检测是否有未采集碎片")
        for pos, value in enumerate(red_point_list):
            red_point_visible_list[pos] = cur_img.getpixel(value)[0] == 247
        have_patch = red_point_visible_list.count(True) > 0
        if have_patch:
            for pos, value in enumerate(red_point_visible_list):
                if value:
                    logger.info("碎片{}未采集，自动采集".format(pos + 1))
                    click_xy(add_point_list[pos])
                    # 分析战力值是否有红色，有说明打不过
                    not_match_attack_target = True  # 未匹配到攻击目标
                    can_attack_pos = None  # 能攻击的下标
                    while not_match_attack_target:
                        temp_img = Image.open(screenshot(temp_dir))
                        for power_pos, power_area in enumerate(power_area_list):
                            if can_attack_pos is None:
                                logger.info("分析第对手【{}】".format(power_pos + 1))
                                have_red = False
                                for x in range(power_area[0], power_area[2]):
                                    if have_red:
                                        break
                                    else:
                                        # 遍历战力值如果有红色，说明打不过，直接切换到下个对手
                                        for y in range(power_area[1], power_area[3]):
                                            if temp_img.getpixel((x, y)) == (252, 62, 62, 255):
                                                logger.info("检测到红色数字，不敌")
                                                have_red = True
                                                break
                                if not have_red:
                                    can_attack_pos = power_pos
                                    not_match_attack_target = False
                            else:
                                logger.info("打得过对手【{}】，发起攻击！".format(can_attack_pos + 1))
                                click_area(power_area_list[can_attack_pos])
                                click_xy(challenge_point)
                                sleep(0.3)
                                click_area(jump_point)
                                sleep(0.2)
                                click_xy(120, 1796)
                                break
                        if not_match_attack_target:
                            logger.info("没一个打得过，刷新对手...")
                            click_area(refresh_point)
                            sleep(0.1)
        else:
            logger.info("未检测到碎片")
            # 检测是否有完成合成按钮
            if cur_img.getpixel(merge_point)[0] == 252:
                logger.info("检测到合成按钮，点击合成")
                click_xy(merge_point)
                sleep(0.2)
                click_xy(merge_point)
                continue
            if cur_img.getpixel(order_point)[0] == 247:
                logger.info("检测到未完成订单，自动点击")
                click_xy(order_point)
                continue
            else:
                logger.info("未检测到待完成订单，任务结束！")
                break

    # 判断是否有订单
    # 点击订单
    # click_xy(821, 204)


if __name__ == '__main__':
    is_dir_existed(temp_dir, is_recreate=True)
    # for i in range(0, 60):
    #     auto_bridge_old()
    #     time.sleep(3)
    # auto_pk()
    screenshot(temp_dir)
    # auto_business()
