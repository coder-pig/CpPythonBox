# -*- coding: utf-8 -*-
# !/usr/bin/env python\
"""
-------------------------------------------------
   File     : bilibili_video_all_download_idm.py
   Author   : CoderPig
   date     : 2023-10-11 18:33
   Desc     : 批量下载B站多P视频，使用idm来下载
-------------------------------------------------
"""
import re
import os

from media.download.video_download import fetch_b_video_list, fetch_mp4_video_url, merge_mp4_wav
from util.download_util import download_idm
from util.file_util import is_dir_existed, write_text_list_to_file, read_list_from_file
from util.logger_util import default_logger
import whisper

logger = default_logger()

# 匹配URL的正则
url_match_pattern = re.compile(r'((ht|f)tps?):\/\/[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:\/~\+#]*[\w\-\@?^=%&\/~\+#])?',
                               re.S)

# 保存文件的目录
output_dir = os.path.join(os.getcwd(), "output")
temp_dir = os.path.join(output_dir, 'temp')
video_dir = os.path.join(output_dir, 'video')
video_correlation_record_file = os.path.join(output_dir, "video_correlation_record.txt")


def init():
    is_dir_existed(output_dir)
    is_dir_existed(temp_dir)
    is_dir_existed(video_dir)


# 利用ffmpeg生成有声音的mp4文件
def generate_mp4_by_ffmpeg():
    for record in read_list_from_file(video_correlation_record_file):
        record_split_list = record.split("\t")
        logger.info("开始合并文件：{}".format(record_split_list))
        merge_mp4_wav(record_split_list[0], record_split_list[1], record_split_list[2])
    logger.info("所有视频合并完毕！")


# 批量下载B站视频
def download_all_video():
    input_url = input("请输入要下载B站视频URL：\n")
    result = url_match_pattern.match(input_url)
    video_record_list = []
    if result is not None:
        if input_url.find("bilibili") != -1:
            v_list = fetch_b_video_list(input_url)
            logger.info("检测到共有视频【{}】集，开始执行批量解析下载...".format(len(v_list)))
            for index, video in enumerate(v_list):
                video_result = fetch_mp4_video_url(video)
                if video_result is not None:
                    video_urls = video_result[0]
                    audio_urls = video_result[1]
                    video_title = "{}、{}".format(index + 1, video.title)
                    logger.info("开始下载：{}".format(video_title))
                    # 直接下载最低画质的
                    b_video_path = download_idm(video_urls[-1][0], input_url, temp_dir, 'mp4', video_title)
                    b_audio_path = download_idm(audio_urls[-1][0], input_url, temp_dir, 'mp4', video_title)
                    after_video_path = os.path.join(video_dir, '{}_after.{}'.format(video_title, 'mp4'))
                    video_record_list.append("{}\t{}\t{}".format(b_video_path, b_audio_path, after_video_path))
            write_text_list_to_file(video_record_list, video_correlation_record_file)
            logger.info("所有音视频下载完毕，请使用ffmepg批量生成mp4文件")
        else:
            exit("检测到非B站链接")
    else:
        exit("URL格式错误，请输入正确的URL")


if __name__ == '__main__':
    init()
    download_all_video()
    # generate_mp4_by_ffmpeg()

    # model = whisper.load_model("tiny")
    # result = model.transcribe("test.mp4", fp16=False, language="Chinese")
    # print(result)
