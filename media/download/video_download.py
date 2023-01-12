# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : video_download.py
   Author   : CoderPig
   date     : 2023-01-12 10:42 
   Desc     : 视频下载，默认采用you_get下载，B站链接支持破解下载(requests或idm)
-------------------------------------------------
"""
import json
import os
import re
import subprocess
import time
from http import cookiejar

import requests as r

from util.download_util import request_download_video, download_idm, you_get_download_video, merge_mp4_wav
from util.file_util import is_dir_existed
from util.logger_util import default_logger

base_url = 'https://www.bilibili.com'
play_url = 'https://api.bilibili.com/x/player/playurl'
page_list_url = 'https://api.bilibili.com/x/player/pagelist'

# 获取视频信息的正则
bv_pattern = re.compile(r'(BV.{10})', re.S)
play_info_pattern = re.compile(r'window\.__playinfo__=(\{.*?\})</script>', re.MULTILINE | re.DOTALL)
initial_state_pattern = re.compile(r'window\.__INITIAL_STATE__=(\{.*?\});', re.MULTILINE | re.DOTALL)
url_match_pattern = re.compile(r'((ht|f)tps?):\/\/[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:\/~\+#]*[\w\-\@?^=%&\/~\+#])?',
                               re.S)

# 保存文件的目录
output_dir = os.path.join(os.getcwd(), "output")
temp_dir = os.path.join(output_dir, 'temp')
video_dir = os.path.join(output_dir, 'video')

# B站Cookie文件
b_cookies = "bilibili.txt"

# 清晰度
support_formats_dict = {
    116: '1080P 60帧',
    80: '1080P 高清',
    64: '720P 60帧',
    32: '480P 清晰',
    16: '360P 流畅'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/83.0.4103.97 Safari/537.36',
    'Origin': base_url
}

cookies_jar = cookiejar.MozillaCookieJar(b_cookies) if os.path.exists(b_cookies) else None
logger = default_logger()


# 初始化方法
def init():
    is_dir_existed(output_dir)
    is_dir_existed(temp_dir)
    is_dir_existed(video_dir)


# B站视频类
class BVideo:
    def __init__(self, title=None, cid=None, bvid=None, avid=None, mp4_url=None, wav_url=None,
                 merge_video=None):
        self.title = title
        self.cid = cid
        self.bvid = bvid
        self.avid = avid
        self.mp4_url = mp4_url
        self.wav_url = wav_url
        self.merge_video = merge_video

    def to_str(self):
        return '{}-{}-{}-{}-{}-{}-{}'.format(self.title, self.cid, self.bvid, self.avid,
                                             self.mp4_url, self.wav_url, self.merge_video)


# 获取B站视频列表
def fetch_b_video_list(url):
    if headers.get("Referer") is not None:
        headers.pop('Referer')
    bv_result = bv_pattern.search(url)
    if bv_result is not None:
        params = {
            'bvid': bv_result.group(1),
            'jsonp': 'jsonp'
        }
        b_video_list = []
        resp = r.get(url=page_list_url, headers=headers, params=params, cookies=cookies_jar)
        logger.info("请求：%s" % resp.url)
        if resp is not None:
            resp_json = resp.json()
            pages_json = resp_json.get('data')
            if pages_json is not None:
                for page in pages_json:
                    b_video = BVideo(bvid=bv_result.group(1))
                    b_video.cid = page['cid']
                    b_video.title = page['part'].replace(' ', '')
                    b_video_list.append(b_video)
                return b_video_list
    else:
        logger.info("URL格式错误")


# 获取B站视频数据
def fetch_b_video_info(url):
    if headers.get("Referer") is not None:
        headers.pop('Referer')
    b_video_list = []
    resp = r.get(url=url, headers=headers, cookies=cookies_jar)
    if resp is not None:
        support_formats_dict_list = []
        resp_text = resp.text
        # 获取支持的清晰度
        play_info_result = play_info_pattern.search(resp_text)
        if play_info_result is not None:
            result_json = json.loads(play_info_result.group(1))
            support_formats_dict_json = result_json['data']['support_formats_dict']
            for support_format in support_formats_dict_json:
                quality = support_formats_dict.get(support_format['quality'])
                if quality is not None:
                    support_formats_dict_list.append(quality)
                else:
                    support_formats_dict_list.append(support_format['quality'])
        initial_result = initial_state_pattern.search(resp_text)
        if initial_result is not None:
            result_json = json.loads(initial_result.group(1))
            video_data = result_json['videoData']
            avid = video_data['aid']
            bvid = video_data['bvid']
            pages_json = video_data.get('pages')
            if pages_json is not None:
                for page_json in pages_json:
                    b_video = BVideo(avid=avid, bvid=bvid)
                    b_video.cid = page_json['cid']
                    b_video.title = page_json['part']
                    b_video_list.append(b_video)
        return support_formats_dict_list, b_video_list


# 获取mp4视频
def fetch_mp4_video_url(b_video):
    params = {
        'cid': b_video.cid,
        'bvid': b_video.bvid,
        'qn': 112,
        'type': '',
        'otype': 'json',
        'fourk': 1,
        'fnver': 0,
        'fnval': 80,
        'avid': b_video.avid
    }
    resp = r.get(url=play_url, params=params, headers=headers, cookies=cookies_jar)
    if resp is not None:
        video_list = []
        audio_list = []
        resp_json = resp.json()
        dash = resp_json['data'].get('dash')
        if dash is not None:
            videos = dash.get('video')
            if videos is not None:
                for video in videos:
                    video_list.append([video['baseUrl'], video['mimeType'], video['codecs'], video['id']])
            audios = dash.get('audio')
            if audios is not None:
                for audio in audios:
                    audio_list.append([audio['baseUrl'], audio['mimeType'], audio['codecs']])
        return video_list, audio_list


# 合并音视频
def merge_mp4_wav(video_path, audio_path, output_path):
    logger.info("音视频合并中~")
    cmd = f'ffmpeg -i {video_path} -i {audio_path} -acodec copy -vcodec copy {output_path}'
    subprocess.call(cmd, shell=True)
    logger.info("合并完毕，输出文件：%s" % output_path)


if __name__ == '__main__':
    init()
    input_url = input("请输入要下载的URL：\n")
    result = url_match_pattern.match(input_url)
    if result is not None:
        if input_url.find("bilibili") != -1:
            logger.info("检测到B站链接，请选择下载方式：\n {}\n1、破解下载\n2、you-get下载\n{}".format('=' * 64, '=' * 64))
        download_type_input = int(input())
        if download_type_input == 1:
            v_list = fetch_b_video_list(input_url)
            logger.info("检测到多P，请输入想要下载的视频序号：")
            logger.info("=" * 64)
            for index, value in enumerate(v_list):
                logger.info('{}、{}'.format(index, value.title))
            logger.info("=" * 64)
            part_choose = int(input())
            if 0 <= part_choose < len(v_list):
                choose_video = v_list[part_choose]
                logger.info("解析：{}".format(choose_video.title))
                video_result = fetch_mp4_video_url(choose_video)
                if video_result is not None:
                    video_urls = video_result[0]
                    audio_urls = video_result[1]
                    if len(video_urls) > 0 and len(audio_urls) > 0:
                        logger.info("检测到多种视频源，请输入想要下载的画质序号：\n{}".format('=' * 64))
                        for index, value in enumerate(video_urls):
                            quality_str = support_formats_dict.get(value[3])
                            logger.info('{}、{} {} {}'.format(index, quality_str, value[1], value[2]))
                        logger.info("=" * 64)
                        video_choose = int(input())
                        bv_video_url = video_urls[video_choose][0]
                        bv_audio_url = audio_urls[0][0]
                        download_type_choose = int(
                            input("请输入下载方式：\n{}\n0、requests\n1、idm\n{}\n".format('=' * 64, '=' * 64)))
                        after_video_path = os.path.join(video_dir, '{}_after.{}'.format(choose_video.title, 'mp4'))
                        if download_type_choose == 0:
                            headers['Referer'] = input_url
                            b_video_path = request_download_video(bv_video_url, headers, temp_dir, 'mp4',
                                                                  choose_video.title)
                            b_audio_path = request_download_video(bv_audio_url, headers, temp_dir, 'mp4',
                                                                  choose_video.title)
                            logger.info("音视频下载完毕，准备合并")
                            merge_mp4_wav(b_video_path, b_audio_path, after_video_path)
                        elif download_type_choose == 1:
                            b_video_path = download_idm(bv_video_url, input_url, temp_dir, 'mp4', choose_video.title)
                            b_audio_path = download_idm(bv_audio_url, input_url, temp_dir, 'mp4', choose_video.title)
                            # idm是异步的，拿不到下载进度，这里休眠30s，避免等下出现文件未合并的情况
                            time.sleep(60)
                            logger.info("音视频下载完毕，准备合并")
                            merge_mp4_wav(b_video_path, b_audio_path, after_video_path)
                        else:
                            logger.info("输出错误")
                            exit(0)
                else:
                    logger.info("无法解析视频源地址")
        elif download_type_input == 2:
            you_get_download_video(input_url, temp_dir, b_cookies)
        else:
            logger.info("检测到非B站链接，默认采用you-get下载")
            you_get_download_video(input_url)
    else:
        logger.info("URL格式错误，请输入正确的URL")
