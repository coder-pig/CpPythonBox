# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : md_local.py
   Author   : CoderPig
   date     : 2025/4/27 09:29
   Desc     : 将md文件本地化的脚本 (将md文件中的图片下载到本地，并更新md文件中的图片链接)
-------------------------------------------------
"""
import re
import os
import requests
import urllib.parse
from pathlib import Path
import hashlib
import time


def download_image(image_url, save_dir):
    """
    下载图片到指定目录
    :param image_url: 图片URL
    :param save_dir: 保存目录
    :return: 本地图片路径
    """
    try:
        # 创建保存目录
        os.makedirs(save_dir, exist_ok=True)

        # 从URL中提取文件名，如果无法提取则使用哈希值作为文件名
        parsed_url = urllib.parse.urlparse(image_url)
        file_name = os.path.basename(parsed_url.path)

        # 如果文件名为空或没有扩展名，使用哈希值+时间戳作为文件名
        if not file_name or '.' not in file_name:
            file_ext = '.png'  # 默认扩展名
            file_name = f"{hashlib.md5(image_url.encode()).hexdigest()}_{int(time.time())}{file_ext}"

        # 本地保存路径
        local_path = os.path.join(save_dir, file_name)

        # 下载图片
        response = requests.get(image_url, stream=True, timeout=10)
        response.raise_for_status()

        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # 返回相对路径
        return os.path.join(os.path.basename(save_dir), file_name)
    except Exception as e:
        print(f"下载图片失败: {image_url}, 错误: {str(e)}")
        return None


def process_markdown_file(md_file_path, img_dir='images', result_file=None):
    """
    处理Markdown文件，下载图片并更新链接
    :param md_file_path: Markdown文件路径
    :param img_dir: 图片保存目录
    :param result_file: 结果文件路径，默认为None，会自动生成
    :return: 处理结果
    """
    if not os.path.exists(md_file_path):
        return f"文件不存在: {md_file_path}"

    # 确保图片目录为相对于Markdown文件的路径
    md_file_dir = os.path.dirname(md_file_path)
    img_save_dir = os.path.join(md_file_dir, img_dir)

    # 设置结果文件路径
    if result_file is None:
        result_file = os.path.join(md_file_dir, "result.md")

    # 读取Markdown文件内容
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配图片链接的正则表达式
    # 匹配 ![alt](url) 或 <img src="url" /> 格式
    img_pattern = r'!\[.*?\]\((http[s]?://[^\s\)]+)\)|<img[^>]+src="(http[s]?://[^\s\"]+)"'

    # 计数器
    count_total = 0
    count_success = 0

    # 查找所有图片链接并替换
    def replace_func(match):
        nonlocal count_total, count_success
        count_total += 1

        # 获取URL (可能在两个捕获组中的一个)
        image_url = match.group(1) if match.group(1) else match.group(2)

        # 下载图片
        local_path = download_image(image_url, img_save_dir)

        if local_path:
            count_success += 1
            # 根据匹配的格式替换URL
            if match.group(1):  # ![alt](url) 格式
                return f"![{match.group(0).split(']')[0][2:]}]({local_path})"
            else:  # <img src="url" /> 格式
                return match.group(0).replace(image_url, local_path)
        else:
            # 下载失败时保留原链接
            return match.group(0)

    # 替换所有图片链接
    new_content = re.sub(img_pattern, replace_func, content)

    # 写入结果文件
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return f"处理完成: 总共 {count_total} 张图片，成功下载 {count_success} 张，结果已保存到 {result_file}"


def batch_process_markdown_files(directory, img_dir='images'):
    """
    批量处理目录下的所有Markdown文件
    :param directory: 目录路径
    :param img_dir: 图片保存目录
    :return: None
    """
    directory = Path(directory)
    if not directory.exists() or not directory.is_dir():
        print(f"目录不存在: {directory}")
        return

    md_files = list(directory.glob('**/*.md'))
    print(f"找到 {len(md_files)} 个Markdown文件")

    for md_file in md_files:
        print(f"处理文件: {md_file}")
        result_file = md_file.with_name(f"result_{md_file.name}")
        result = process_markdown_file(str(md_file), img_dir, str(result_file))
        print(result)
        print("-" * 50)


if __name__ == '__main__':
    # 直接指定要处理的Markdown文件路径
    md_file_path = "origin.md"

    # 指定图片保存目录名称
    img_dir = 'images'

    # 处理单个文件，结果保存为result.md
    result = process_markdown_file(md_file_path, img_dir)
    print(result)

    # 如果需要批量处理目录中的所有Markdown文件，取消下面的注释并注释上面的单文件处理代码
    # md_directory = "markdown/backups"
    # batch_process_markdown_files(md_directory, img_dir)