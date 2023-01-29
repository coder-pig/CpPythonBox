# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : pic_util.py
   Author   : CoderPig
   date     : 2022-12-23 14:59 
   Desc     : 图片处理工具
-------------------------------------------------
"""
import os
import time
import numpy as np
from PIL import Image, ImageDraw


def get_picture_size(pic_path):
    """
    获得图片尺寸
    :param pic_path: 图片路径
    :return: 图片宽度、图片高度，图片格式，返回样例：(1080, 1080, 'JPEG')
    """
    img = Image.open(pic_path)
    return img.width, img.height, img.format


def crop_area(pic_path, save_dir, start_x, start_y, end_x, end_y):
    """
    裁剪图片
    :param save_dir: 保存路径
    :param pic_path: 图片路径
    :param start_x: x轴起始坐标
    :param start_y: y轴起始坐标
    :param end_x: x轴终点坐标
    :param end_y: y轴终点坐标
    :return: 生成的截图路径
    """
    img = Image.open(pic_path)
    region = img.crop((start_x, start_y, end_x, end_y))
    save_path = os.path.join(save_dir, "crop_" + str(round(time.time() * 1000)) + ".png")
    region.save(save_path)
    print(save_path)
    return save_path


def resize_picture(pic_path, width, height):
    """
    调整图片分辨率
    :param pic_path: 图片路径
    :param width: 调整后的图片宽
    :param height: 调整后的图片高
    :return: 调整后的图片路径
    """
    img = Image.open(pic_path)
    resized_img = img.resize((width, height), Image.ANTIALIAS)
    save_path = os.path.join(os.getcwd(), "resized_" + str(round(time.time() * 1000)) + ".png")
    resized_img.save(save_path)
    return save_path


def resize_picture_percent(pic_path, percent):
    """
    按比例调整图片分辨率
    :param pic_path: 图片路径
    :param percent: 缩放比例
    :return: 调整后的图片路径
    """
    img = Image.open(pic_path)
    resized_img = img.resize((int(img.width * percent), int(img.height * percent)), Image.ANTIALIAS)
    save_path = os.path.join(os.getcwd(), "resized_" + str(round(time.time() * 1000)) + ".png")
    resized_img.save(save_path)
    return save_path


def picture_to_gray(pic_path, save_dir):
    """
    转灰度图
    :param save_dir:
    :param pic_path: 图片路径
    :return: 转换后的图片路径
    """
    img = Image.open(pic_path)
    gray_img = img.convert('L')
    save_path = os.path.join(save_dir, "gray_" + str(round(time.time() * 1000)) + ".png")
    gray_img.save(save_path)
    return save_path


def picture_to_black_white(pic_path, save_dir, threshold=127):
    """
    图片二值化(黑白)
    :param save_dir:
    :param pic_path: 图片路径
    :param threshold:  灰度阈值，默认127
    :return: 转换后的图片路径
    """
    img = Image.open(pic_path)
    save_path = os.path.join(save_dir, "bw_" + str(round(time.time() * 1000)) + ".png")
    if threshold == 127:
        img.convert('1').save(save_path)
    else:
        img.convert('L').point([0 if x < threshold else 1 for x in range(256)], '1').save(save_path)
    return save_path


def t2val(value, threshold):
    return 0 if value < threshold else 1


if __name__ == '__main__':
    print(get_picture_size('test_ocr.jpg'))
    print(crop_area('test_ocr.jpg', os.getcwd(), 0, 0, 100, 200))
    print(resize_picture('test_ocr.jpg', 300, 600))
    print(resize_picture_percent('test_ocr.jpg', 0.5))
    print(picture_to_gray('test_ocr.jpg', os.getcwd()))
    print(picture_to_black_white('test_ocr.jpg', os.getcwd()))
