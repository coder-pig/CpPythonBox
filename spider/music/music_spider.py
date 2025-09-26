# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : music_spider.py
   Author   : CoderPig
   date     : 2024-05-09 17:14
   Desc     : 艺人粉丝爬取
-------------------------------------------------
"""
import datetime
import json
import os
import random
import re
import shutil
import threading
import time

import PySimpleGUI as psgui
import requests as r
import urllib3
import xlwt
from NeteaseCloudMusic import NeteaseCloudMusicApi

urllib3.disable_warnings()
lock = threading.RLock()

artist_config_file = "artist_config.json"  # 艺人配置信息文件(主要是id)
artist_config_dict = {}  # 艺人配置信息字典，兼是歌手名
retry_count = 0  # 错误重试次数，最多重试三次

# songstats.com
songstats_request_headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Fe-Platform": "web",
    "Fe-Version": "143",
    "Origin": "https://songstats.com",
    "Priority": "u=1, i",
    "Referer": "https://songstats.com/artist/tlkbdfvq/matt-maltese?source=radio",
    "Sec-Ch-Ua": "\"Chromium\";v=\"124\", \"Microsoft Edge\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 "
                  "Safari/537.36 Edg/124.0.0.0",
}

# QQ 音乐
qq_music_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
                  "Version/16.6 Mobile/15E148 Safari/604.1"
}

qq_data_url = "https://i.y.qq.com/n2/m/share/profile_v2/index.html?ADTAG=ryqq.singer&source=ydetail&singermid={}"

qq_follower_pattern = re.compile(r'fansNum.*?(\d+)')


# 判断文件是否存在
def if_file_existed(file_path):
    return os.path.exists(file_path)


# 判断文件是否存在，不存在则创建
def is_dir_existed(file_path, mkdir=True, is_recreate=False):
    if mkdir:
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        else:
            if is_recreate:
                delete_file(file_path)
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
    else:
        return os.path.exists(file_path)


# 删除文件
def delete_file(file_path):
    del_list = os.listdir(file_path)
    for f in del_list:
        delete_path = os.path.join(file_path, f)
        if os.path.isfile(delete_path):
            os.remove(delete_path)
        elif os.path.isdir(delete_path):
            shutil.rmtree(delete_path)


# 文本的形式读取文件
def read_file_text_content(file_path):
    if not os.path.exists(file_path):
        return None
    else:
        with open(file_path, 'r+', encoding='utf-8') as f:
            return f.read()


# 按行的形式读取文件内容
def read_list_from_file(file_path):
    if os.path.exists(file_path):
        data_list = []
        with open(file_path, "r+", encoding='utf-8') as f:
            for ip in f:
                data_list.append(ip.replace("\n", ""))
        return data_list


def write_text_to_file(content, file_path, mode="w+"):
    """ 将文字写入到文件中

    Args:
        content (str): 文字内容
        file_path (str): 写入文件路径
        mode (str): 文件写入模式，w写入、a追加、+可读写

    Returns:
        None
    """
    with lock:
        try:
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content + "\n", )
        except OSError as reason:
            print(str(reason))


class ArtistInfo:
    def __init__(self, artist_name=None, songstats_id=None,
                 spotify_monthly_listeners=None, spotify_followers=None,
                 spotify_popularity=None,
                 spotify_artist_rank=None, deezer_followers=None, deezer_popularity=None, soundcloud_followers=None,
                 tiktok_followers=None, instagram_followers=None, youtube_subscribers=None,
                 wwy_id=None, wyy_followers=None,
                 qq_id=None, qq_followers=None, error_info=None):
        self.artist_name = artist_name
        self.songstats_id = songstats_id
        self.spotify_monthly_listeners = spotify_monthly_listeners
        self.spotify_followers = spotify_followers
        self.spotify_popularity = spotify_popularity
        self.spotify_artist_rank = spotify_artist_rank
        self.deezer_followers = deezer_followers
        self.deezer_popularity = deezer_popularity
        self.soundcloud_followers = soundcloud_followers
        self.tiktok_followers = tiktok_followers
        self.instagram_followers = instagram_followers
        self.youtube_subscribers = youtube_subscribers
        self.wwy_id = wwy_id
        self.wyy_followers = wyy_followers
        self.qq_id = qq_id
        self.qq_followers = qq_followers
        self.error_info = error_info

    def __str__(self):
        # 属性添加\n拼接
        return json.dumps(self.__dict__, ensure_ascii=False)


def fetch_wwy_followers():
    netease_cloud_music_api = NeteaseCloudMusicApi()
    version_result = netease_cloud_music_api.request("/artist/follow/count", {'id': '2116'})
    return version_result['data']['data']['fansCnt']


def fetch_qq_followers(singermid):
    resp = r.get(qq_data_url.format(singermid), headers=qq_music_headers)
    if resp:
        match = qq_follower_pattern.search(resp.text)
        if match:
            return match.group(1)



# 判断key存在执行对应的逻辑
def assign_if_key_exists(data_dict, key, assign_func):
    value = data_dict.get(key)
    if value is not None and value != '':
        assign_func(value)


def assign_attribute_if_key_exists(obj, data_dict, key, attribute_name):
    assign_if_key_exists(data_dict, key, lambda x: setattr(obj, attribute_name, x))


# 爬取网易云的艺人信息
def fetch_wwy_artist_info(artist_info, print_gui):
    print_gui.print("抓取【{}】的网易云粉丝数据...".format(artist_info.artist_name))
    netease_cloud_music_api = NeteaseCloudMusicApi()
    # 艺人id为None或空字符串先获取id
    if artist_info.wwy_id is None or artist_info.wwy_id == "":
        print_gui.print("未获得【{}】的网易云ID，执行搜索...".format(artist_info.artist_name))
        search_result = netease_cloud_music_api.request("/cloudsearch",
                                                        {'keywords': artist_info.artist_name, "type": 100})
        if search_result:
            if not isinstance(search_result['data'], str) and search_result['data'].get('result'):
                artists_list = search_result['data']['result'].get("artists")
                if artists_list and len(artists_list) > 0:
                    artist_info.wwy_id = artists_list[0]['id']
                    artist_config_dict[artist_info.artist_name]['wwy_id'] = artist_info.wwy_id
                else:
                    artist_info.error_info = "未搜索到艺人的网易云ID"
    else:
        print_gui.print("已获得【{}】的网易云ID，获取粉丝数据...".format(artist_info.artist_name))

    # 拿到艺人id后爬取艺人信息
    if artist_info.wwy_id and artist_info.wwy_id != "":
        follower_result = netease_cloud_music_api.request("/artist/follow/count", {'id': artist_info.wwy_id})
        artist_info.wyy_followers = follower_result['data']['data']['fansCnt']
    else:
        artist_info.error_info = "获取不到艺人的网易云粉丝数据ID，请检查名字是否正确"


# 爬取songstats的艺人信息
def fetch_songstats_artist_info(artist_info, print_gui):
    global retry_count
    try:
        print_gui.print("抓取【{}】的Songstats粉丝数据...".format(artist_info.artist_name))
        # 艺人id为None或空字符串先获取id
        if artist_info.songstats_id is None or artist_info.songstats_id == "":
            print_gui.print("未获得【{}】的网易云ID，执行搜索...".format(artist_info.artist_name))

            songstats_artist_search_url = "https://data.songstats.com/api/v1/subscriptions/artist_label_search"
            songstats_artist_search_resp = r.get(songstats_artist_search_url, headers=songstats_request_headers,
                                                 params={"q": artist_info.artist_name, "type": "top"}, verify=False)
            if songstats_artist_search_resp:
                songstats_artist_search_json = songstats_artist_search_resp.json()
                artists_list = songstats_artist_search_json.get("artists")
                if artists_list and len(artists_list) > 0:
                    artist_info.songstats_id = artists_list[0]["idUnique"]
                    artist_config_dict[artist_info.artist_name]['songstats_id'] = artist_info.songstats_id
        else:
            print_gui.print("已获得【{}】的Songstats ID，获取粉丝数据...".format(artist_info.artist_name))
        if artist_info.songstats_id is None or artist_info.songstats_id == "":
            artist_info.error_info = "获取不到艺人的Songstats id"
        else:
            # 拿到艺人id后爬取艺人信息
            songstats_data_url = (
                "https://data.songstats.com/api/v1/analytics/multi_entity_stat_overview?sources=overview"
                "&forWidget=false&idUnique={}")
            songstats_data_resp = r.get(songstats_data_url.format(artist_info.songstats_id),
                                        headers=songstats_request_headers, verify=False)
            if songstats_data_resp:
                songstats_data_json = songstats_data_resp.json()
                songstats_data_dict = {}
                for data in songstats_data_json["data"]:
                    songstats_data_dict[data["source"]] = data['data']
                spotify_data = songstats_data_dict.get('spotify')
                if spotify_data:
                    assign_attribute_if_key_exists(artist_info, spotify_data, "monthlyListenersCurrent",
                                                   "spotify_monthly_listeners")
                    assign_attribute_if_key_exists(artist_info, spotify_data, "followersTotal", "spotify_followers")
                    assign_attribute_if_key_exists(artist_info, spotify_data, "popularityCurrent", "spotify_popularity")
                deezer_data = songstats_data_dict.get('deezer')
                if deezer_data:
                    assign_attribute_if_key_exists(artist_info, deezer_data, "followersTotal", "deezer_followers")
                    assign_attribute_if_key_exists(artist_info, deezer_data, "popularityCurrent", "deezer_popularity")
                soundcloud_data = songstats_data_dict.get('soundcloud')
                if soundcloud_data:
                    assign_attribute_if_key_exists(artist_info, soundcloud_data, "followersTotal",
                                                   "soundcloud_followers")
                tiktok_data = songstats_data_dict.get('tiktok')
                if tiktok_data:
                    assign_attribute_if_key_exists(artist_info, tiktok_data, "likesTotal", "tiktok_followers")
                instagram_data = songstats_data_dict.get('instagram')
                if instagram_data:
                    assign_attribute_if_key_exists(artist_info, instagram_data, "followersTotal", "instagram_followers")
                youtube_data = songstats_data_dict.get('youtube')
                if youtube_data:
                    assign_attribute_if_key_exists(artist_info, youtube_data, "subscribersTotal", "youtube_subscribers")
            else:
                artist_info.error_info = "获取不到艺人的Songstats数据"
            # 艺人排行需要另外查接口
            songstats_chart_url = "https://data.songstats.com/api/v1/analytics/chart?idUnique={}&source=spotify"
            songstats_chart_resp = r.get(songstats_chart_url.format(artist_info.songstats_id),
                                         headers=songstats_request_headers, verify=False)
            if songstats_chart_resp:
                songstats_chart_json = songstats_chart_resp.json()
                icon_data_list = songstats_chart_json['chart']['iconData']
                if icon_data_list and len(icon_data_list) > 0:
                    for icon_data in icon_data_list:
                        if icon_data['text'] == 'Artist Rank':
                            artist_info.spotify_artist_rank = icon_data.get('count')
            else:
                artist_info.error_info = "获取不到艺人的排行数据"
    except Exception as e:
        if retry_count < 3:
            print_gui.print("数据爬取异常，休眠5~8秒后重试 → {}".format(e))
            time.sleep(random.randint(5, 8))
            fetch_songstats_artist_info(artist_info, print_gui)
            retry_count += 1
        else:
            retry_count = 0
            artist_info.error_info = str(e)


# 艺人配置信息类
class ArtistConfig:
    def __init__(self, artist_name, songstats_id, wwy_id, qq_id):
        self.artist_name = artist_name
        self.songstats_id = songstats_id
        self.wwy_id = wwy_id
        self.qq_id = qq_id

    # 生成json字符串的方法
    def to_json(self):
        return json.dumps(self.__dict__, ensure_ascii=False)


# 生成艺人数据表格
def generate_excel(artist_result_list):
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet("粉丝数据")
    header_list = ["艺人", "Monthly Listeners", "Followers", "Popularity", "Artist Rank", "Deezer Followers",
                   "Deezer Popularity", "SoundCloud", "TikTok", "Instagram", "YouTube",
                   "网易云", "QQ音乐", "错误信息"]
    # 写入表头
    for pos, header in enumerate(header_list):
        worksheet.write(0, pos, label=header)
    # 写入表数据
    for row, artist_info in enumerate(artist_result_list):
        worksheet.write(row + 1, 0, label=artist_info.artist_name)
        worksheet.write(row + 1, 1, label=artist_info.spotify_monthly_listeners)
        worksheet.write(row + 1, 2, label=artist_info.spotify_followers)
        worksheet.write(row + 1, 3, label=artist_info.spotify_popularity)
        worksheet.write(row + 1, 4, label=artist_info.spotify_artist_rank)
        worksheet.write(row + 1, 5, label=artist_info.deezer_followers)
        worksheet.write(row + 1, 6, label=artist_info.deezer_popularity)
        worksheet.write(row + 1, 7, label=artist_info.soundcloud_followers)
        worksheet.write(row + 1, 8, label=artist_info.tiktok_followers)
        worksheet.write(row + 1, 9, label=artist_info.instagram_followers)
        worksheet.write(row + 1, 10, label=artist_info.youtube_subscribers)
        worksheet.write(row + 1, 11, label=artist_info.wyy_followers)
        worksheet.write(row + 1, 12, label=artist_info.qq_followers)
        worksheet.write(row + 1, 13, label=artist_info.error_info)
    workbook.save("艺人粉丝数据_{}.xls".format(datetime.datetime.now().strftime("%Y年%m月%d日_%H-%M-%S")))
    # 将artist_config_dict保存为json文件
    write_text_to_file(json.dumps(list(artist_config_dict.values()), ensure_ascii=False), artist_config_file)


# 爬取艺人的具体执行方法
def artist_spider(artist_name, print_gui):
    # 艺人信息类
    artist_info = ArtistInfo(artist_name)

    # 读取艺人配置信息
    artist_config = artist_config_dict.get(artist_name)
    if artist_config:
        if artist_config.get('songstats_id') is not None and artist_config['songstats_id'] != "":
            artist_info.songstats_id = artist_config['songstats_id']
        if artist_config.get('wwy_id') is not None and artist_config['wwy_id'] != "":
            artist_info.wwy_id = artist_config['wwy_id']
        if artist_config.get('qq_id') is not None and artist_config['qq_id'] != "":
            artist_info.qq_id = artist_config['qq_id']
    else:
        artist_config_dict[artist_name] = {'artist_name': artist_name}
    fetch_songstats_artist_info(artist_info, print_gui)
    fetch_wwy_artist_info(artist_info, print_gui)
    return artist_info


# 爬虫执行的具体入口
def start_spider(artist_list_file, print_gui):
    artist_name_list = read_list_from_file(artist_list_file)
    # 艺人爬取结果列表
    artist_result_list = []
    # 读取歌手配置文件
    if if_file_existed(artist_config_file):
        artist_json_list = json.loads(read_file_text_content(artist_config_file))
        for artist_json in artist_json_list:
            artist_config_dict[artist_json['artist_name']] = artist_json
    else:
        print_gui.print("未检测到艺人配置文件...")
    for artist_name in artist_name_list[:200]:
        artist_result_list.append(artist_spider(artist_name, print_gui))
    generate_excel(artist_result_list)


# 主题初始化
def theme_init():
    psgui.theme_background_color("#CC2529")  # 窗口背景色
    psgui.theme_text_color("#EFF0DB")  # 文本框字体颜色
    psgui.theme_text_element_background_color("#CC2529")  # 文本框背景颜色
    psgui.theme_button_color("#E35439")  # 按钮背景颜色
    psgui.theme_element_background_color("#CC2529")  # 设置结点背景颜色
    psgui.set_global_icon("rabbit.ico")  # 设置窗口图标


def main_gui():
    layout_control = [
        [
            psgui.Frame(layout=[
                [psgui.FileBrowse("选择文件", key='file_browser', enable_events=True)]
            ], title="请选择要抓取艺人的.txt文件"),
            psgui.Frame(layout=[
                [psgui.Text("", key="file_path")]
            ], title="当前选中文件"),
            psgui.Button("开始爬取", key="transform")
        ],[
            [psgui.Multiline(size=(80, 20), key='-OUTPUT-', autoscroll=True)],
        ]
    ]
    window_panel = psgui.Window('艺人粉丝爬取', layout_control)
    while True:
        event, value = window_panel.read()
        if event == psgui.WIN_CLOSED:
            break
        if event == 'file_browser':
            # 判断选择的是否为md文件，不是弹窗
            file_path = value[event]
            if file_path.endswith('.txt'):
                window_panel['file_path'].update(file_path)
            else:
                psgui.popup("错误", "请选择.txt结尾的文件")
        if event == 'transform':
            # start_spider(window_panel['file_path'].DisplayText, window_panel['-OUTPUT-'])
            threading.Thread(target=start_spider,
                             args=(window_panel['file_path'].DisplayText, window_panel['-OUTPUT-'])).start()
    window_panel.close()


if __name__ == '__main__':
    # 艺术家id：1l6fg750、tlkbdfvq
    # fetch_artist_info("1l6fg750")
    # fetch_qq_followers("0025NhlN2yWrP4")
    # search_qq_artist("PJ Harvey")
    # start_spider("240510IAG1.txt")
    theme_init()
    main_gui()
