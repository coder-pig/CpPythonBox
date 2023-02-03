# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : sssf_spring.py
   Author   : CoderPig
   date     : 2023-02-03 15:12 
   Desc     : 谁是首富(春节活动相关代码)
-------------------------------------------------
"""


# 春节自动答题(对联)
from PIL import Image
from pyppeteer import launch

from util.file_util import get_temp_save_root_path
from util.ocr_util import picture_local_ocr
from util.pic_util import picture_to_gray, crop_area, join_two_picture, picture_to_black_white
import re

chinese_pattern = re.compile(".*?([\u4e00-\u9fa5]+)", re.S)  # 筛选中文的正则
temp_dir = get_temp_save_root_path()


def auto_spring_answer(picture):
    # 题库
    answer_dict = {
        "一": ["四季财原顺意来", "万事如意福临门"],
        "千": ["万户彩灯红"],
        "四": ["八节永平安"],
        "山": ["水清百鸟争春"],
        "人": ["思发在花前"],
        "大": ["门庭喜气新"],
        "平": ["人顺家和万事兴"],
        "日": ["春来江水绿如蓝"],
        "去": ["花市灯如昼"],
        "年": ["春早福满门"],
        "合": ["内外平安好运来"],
        "家": ["春浓日暖花香"],
        "新": ["佳年顺景财源来", "佳岁平安步步高"],
        "卯": ["兔岁报新春"],
        "爆": ["春风送暖入屠苏", "桃符万户更新", "红梅朵朵迎新春"],
        "时": ["好花应时而开"],
        "春": ["岁月赋诗情", "花信早传梅", "福由兔口衔来", "红梅点点绣千山", "节至人间万象新"],
        "青": ["绿水溢春华"],
        "绿": ["红梅正报万家春"],
        "瑞": ["花兔起舞贺吉祥", "花兔起舞贺新年"]
    }
    # 识别上联的第一个字
    first_word_dict = picture_local_ocr(picture_to_gray(crop_area(picture, temp_dir, 50, 497, 201, 630), temp_dir))
    first_word = list(first_word_dict.keys())[0]
    # 识别下联
    second_couplet_dict = picture_local_ocr(
        picture_to_gray(crop_area(picture, temp_dir, 886, 506, 1032, 1396), temp_dir))
    second_couplet = list(second_couplet_dict.keys())[0] if len(list(second_couplet_dict.keys())) > 0 else ""
    # 识别备选词
    choose_words_dict = picture_local_ocr(
        picture_to_gray(crop_area(picture, temp_dir, 40, 1750, 1012, 2160), temp_dir))
    choose_words = second_couplet + list(choose_words_dict.keys())[0]
    word_count, couplet = 0, None
    for key in answer_dict.keys():
        if key in first_word:
            # 遍历下联
            for answer in answer_dict.get(key):
                count = 0
                for word in choose_words:
                    if word in answer:
                        count += 1
                if word_count < count:
                    word_count, couplet = count, answer
    print("最终匹配到的下联：{}".format(couplet))
    # print(picture_local_ocr(crop_area("c1.jpg", temp_dir, 50, 497, 201, 620)))
    # print(picture_local_ocr(crop_area("c1.jpg", temp_dir, 50, 497, 201, 620)))

    # ocr = BaiDuOCR()
    # while True:
    #     input()
    #     orc_result = ocr.general(crop_area(screenshot(temp_dir), temp_dir, 44, 497, 194, 1403))
    #     webbrowser.open("https://www.baidu.com/s?wd={}下一句".format(orc_result))
    # crop_area("c6.jpg", temp_dir, 886, 505, 1032, 1396)
    # crop_area("c6.jpg", temp_dir, 78, 1750, 1027, 2022)

    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 '
    #                   'Safari/537.36 '
    # }

    # 春节自动答题(对联)
    # def auto_spring_answer():
    #     first_couplet = extract_couplet()
    #     asyncio.get_event_loop().run_until_complete(get_source_code(first_couplet))
    # while True:
    #     input()
    #     first_couplet = extract_couplet()
    #     webbrowser.open("https://www.baidu.com/s?wd={}的下联".format(first_couplet))


async def get_source_code(first_couplet):
    browser = await launch()
    page = await browser.newPage()
    await page.goto("https://www.baidu.com/s?wd={}".format(first_couplet))
    content = await page.content()
    match_pattern = re.compile(r"{}[,，]?([\u4e00-\u9fa5]{{{count}}})".format(first_couplet, count=len(first_couplet)),
                               re.S)
    match_result_list = re.findall(match_pattern, content)
    result_set = set()
    for match_result in match_result_list:
        result_set.add(match_result)
    if len(result_set) > 0:
        print("{} 检索到【{}】的可选下联如下 {}".format("=" * 16, first_couplet, "=" * 16))
        for pos, result in enumerate(result_set):
            print("{}、{}".format(pos + 1, result))
    else:
        print("未检索到【{}】的可选下联".format(first_couplet))
    await browser.close()


def extract_couplet():
    first_pic = crop_area("c4.jpg", temp_dir, 50, 497, 201, 1402)
    second_pic = crop_area("c4.jpg", temp_dir, 886, 506, 1032, 1396)
    orc_result_dict = picture_local_ocr(
        picture_to_gray(join_two_picture(first_pic, second_pic, temp_dir, 400), temp_dir))
    first_sentence = ""
    second_sentence = ""
    for orc_result_key in orc_result_dict.keys():
        match_result = chinese_pattern.search(orc_result_key)
        if int(orc_result_dict.get(orc_result_key)[0]) <= 151:
            if match_result:
                first_sentence += (match_result.group(1))
        else:
            if match_result:
                second_sentence += (match_result.group(1))
    return first_sentence


def search_area_position():
    origin_img = Image.open(picture_to_black_white("c5.jpg", temp_dir, 130))
    w, h = origin_img.size
    second_couplet_area = (886, 506, 1032, 1396)  # 第二个对联的区域，直接遍历这个区域接口
    half_width = int((1032 - 886) / 2)  # 连续白色直线需超过一半的宽度
    # 水平
    horizontal_first_point_list = []
    horizontal_second_point_list = []
    for y in range(second_couplet_area[1], second_couplet_area[3]):
        first_white_point = None  # 起始白色点
        second_white_point = None  # 结束白色点
        for x in range(second_couplet_area[0], second_couplet_area[2]):
            if origin_img.getpixel((x, y)) == 255:
                if first_white_point is None:
                    first_white_point = [x, y]
                else:
                    second_white_point = [x, y]
            else:
                if first_white_point is not None and second_white_point is not None:
                    distance = second_white_point[0] - first_white_point[0]
                    if distance > half_width:
                        horizontal_first_point_list.append(first_white_point)
                        horizontal_second_point_list.append(second_white_point)
                    first_white_point = None
                    second_white_point = None
    # 垂直
    vertical_first_point_list = []
    vertical_second_point_list = []
    for x in range(second_couplet_area[0], second_couplet_area[2]):
        first_white_point = None  # 起始白色点
        second_white_point = None  # 结束白色点
        for y in range(second_couplet_area[1], second_couplet_area[3]):
            if origin_img.getpixel((x, y)) == 255:
                if first_white_point is None:
                    first_white_point = [x, y]
                else:
                    second_white_point = [x, y]
            else:
                if first_white_point is not None and second_white_point is not None:
                    distance = second_white_point[1] - first_white_point[1]
                    if distance > half_width:
                        vertical_first_point_list.append(first_white_point)
                        vertical_second_point_list.append(second_white_point)
                    first_white_point = None
                    second_white_point = None

    point_list = []
    for h_pos in range(0, len(horizontal_first_point_list)):
        for v_pos in range(0, len(vertical_first_point_list)):
            if horizontal_first_point_list[h_pos][0] <= vertical_first_point_list[v_pos][0] <= \
                    horizontal_second_point_list[h_pos][0] \
                    and vertical_first_point_list[v_pos][1] <= horizontal_first_point_list[h_pos][1] <= \
                    vertical_second_point_list[v_pos][1]:
                point_list.append((vertical_first_point_list[v_pos][0], horizontal_first_point_list[h_pos][1]))
    new_img = Image.new('L', (w, h), "white")
    middle_x = int((886 + 1032) / 2)
    start_point_dict = {}
    end_point_dict = {}
    for point in point_list:
        if point[0] <= middle_x:
            if start_point_dict.get(point[1]) is None:
                start_point_dict[point[1]] = set()
            start_point_dict[point[1]].add(point[0])
        else:
            if end_point_dict.get(point[1]) is None:
                end_point_dict[point[1]] = set()
            end_point_dict[point[1]].add(point[0])
    x_point_dict = {}
    for point_key in start_point_dict.keys():
        # 右侧没有匹配的y值直接跳过
        if end_point_dict.get(point_key) is None:
            continue
        is_match = False
        for start_x in start_point_dict[point_key]:
            # 每行只需要一对点
            if not is_match:
                for end_x in end_point_dict[point_key]:
                    if end_x - start_x > half_width:
                        if x_point_dict.get(start_x) is None:
                            x_point_dict[start_x] = []
                        x_point_dict[start_x].append(point_key)
                        if x_point_dict.get(end_x) is None:
                            x_point_dict[end_x] = []
                        x_point_dict[end_x].append(point_key)
                        is_match = True
                        break
            else:
                break
    # 坐标升序排列
    x_point_sort_list = sorted(x_point_dict.items(), key=lambda item: item[0])
    second_pos = -1
    for pos in range(1, len(x_point_sort_list) - 1):
        if x_point_sort_list[pos][0] - x_point_sort_list[pos - 1][0] > 20:
            second_pos = pos
    first_y_point_list = []
    second_y_point_list = []
    for pos, value in enumerate(x_point_sort_list):
        if pos < second_pos:
            first_y_point_list += value[1]
        else:
            second_y_point_list += value[1]
    # 坐标点升序排列
    list.sort(first_y_point_list)
    list.sort(second_y_point_list)
    # 左边点和右边点的x坐标
    start_x = x_point_sort_list[0][0]
    end_x = x_point_sort_list[second_pos][0]
    # 遍历y周间隔超过20的点
    final_start_point_list = [(start_x, first_y_point_list[0])]
    for pos in range(1, len(first_y_point_list) - 1):
        if first_y_point_list[pos] - first_y_point_list[pos - 1] > 20:
            final_start_point_list.append((start_x, first_y_point_list[pos]))
            pos += 1
    # 右侧点的遍历，其实可以省略的，因为y轴是对称的，这里只是为了更直观
    final_end_point_list = [(end_x, second_y_point_list[0])]
    for pos in range(1, len(second_y_point_list) - 1):
        if second_y_point_list[pos] - second_y_point_list[pos - 1] > 20:
            final_end_point_list.append((end_x, second_y_point_list[pos]))
            pos += 1
    print(final_start_point_list)
    print(final_end_point_list)
    # 把正方形绘制到图片上
    for pos in range(0, len(final_end_point_list), 2):
        for y in range(final_start_point_list[pos][1], final_start_point_list[pos + 1][1]):
            new_img.putpixel((start_x, y), 0)
            new_img.putpixel((end_x, y), 0)
        for x in range(start_x, end_x):
            new_img.putpixel((x, final_start_point_list[pos][1]), 0)
            new_img.putpixel((x, final_end_point_list[pos + 1][1]), 0)

    new_img.save("white.png")

    # 按照y轴点长度排序

    # 前两项即为前后两个点的列表
    first_y_point_set = set()
    second_y_point_list = set()
    # 突变下标

    # for x_point in x_point_sort_list:
    #     print(x_point)
    # # 前两项即为前后两个点的列表
    # first_y_point_list = x_point_sort_list[0][1]
    # second_y_point_list = x_point_sort_list[1][1]
    # # 最终的点列表，第一个点肯定是
    # final_point_list = [(x_point_sort_list[0][0], first_y_point_list[0])]
    # first_pos = 0
    # while True:
    #     if first_pos < len(first_y_point_list) - 1:
    #         # 前后点间距大于10说明就是跳跃点
    #         if first_y_point_list[first_pos] + 10 < first_y_point_list[first_pos + 1]:
    #             final_point_list.append((x_point_sort_list[0][0], first_y_point_list[first_pos]))
    #             final_point_list.append((x_point_sort_list[0][0], first_y_point_list[first_pos + 1]))
    #             first_pos += 2
    #         else:
    #             first_pos += 1
    #     else:
    #         break
    # # 第二组第一个点也肯定是
    # final_point_list.append((x_point_sort_list[1][0], second_y_point_list[0]))
    # second_pos = 0
    # while True:
    #     if second_pos < len(second_y_point_list) - 1:
    #         # 前后点间距大于10说明就是跳跃点
    #         if second_y_point_list[second_pos] + 10 < second_y_point_list[second_pos + 1]:
    #             final_point_list.append((x_point_sort_list[1][0], second_y_point_list[second_pos]))
    #             final_point_list.append((x_point_sort_list[1][0], second_y_point_list[second_pos + 1]))
    #         second_pos += 1
    #     else:
    #         break
    # for pos, value in enumerate(final_point_list):
    #     new_img.putpixel(value, 0)

    # for pos in range(0, len(horizontal_first_point_list)):
    #     for x in range(horizontal_first_point_list[pos][0], horizontal_second_point_list[pos][0]):
    #         new_img.putpixel((x, horizontal_first_point_list[pos][1]), 0)
    # for pos in range(0, len(vertical_first_point_list)):
    #     for y in range(vertical_first_point_list[pos][1], vertical_second_point_list[pos][1]):
    #         new_img.putpixel((vertical_first_point_list[pos][0], y), 0)
    # point_dict = {}
    # for point in point_list:
    #     if point_dict.get(point[0]) is None:
    #         point_dict[point[0]] = []
    #     point_dict[point[0]].append(point)
    # max_length_start_list = []
    # max_length_end_list = []
    # for point_key in point_dict.keys():
    #     if len(point_dict[point_key]) > len(max_length_start_list)
    #
    # for point_key in point_dict.keys():
    #     print("{}、{}".format(point_key, point_dict[point_key]))
