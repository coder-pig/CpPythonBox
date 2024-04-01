# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : xj_api.py
   Author   : CoderPig
   date     : 2023-11-06 16:10
   Desc     : 调用录音转文字(迅捷) API获取字幕
-------------------------------------------------
"""
import hashlib
import math
import os
import time

import requests

from config_getter import get_configs, update_configs
from util.file_util import is_dir_existed, write_text_list_to_file, search_all_file
from util.logger_util import default_logger

logger = default_logger()
input_dir = os.path.join(os.getcwd(), "input")
output_dir = os.path.join(os.getcwd(), "output")
xj_input_dir = os.path.join(input_dir, "xj")
xj_output_dir = os.path.join(output_dir, "xj")
mp3_save_dir = os.path.join(xj_output_dir, 'mp3')
srt_save_dir = os.path.join(xj_output_dir, 'srt')
txt_save_dir = os.path.join(xj_output_dir, 'txt')

# 读取配置元组
config_tuple = get_configs('xj-api', ('host', 'product_info', 'software_name', 'device_id', 'account', 'user_token'))

# 对应配置
host = config_tuple[0]
product_info = config_tuple[1]
software_name = config_tuple[2]
device_id = config_tuple[3]
account = config_tuple[4]
user_token = config_tuple[5]

# API接口
base_url = 'https://{}/api/v4/'.format(host)
check_token_url = base_url + "checktoken"
safe_sms_verify_url = base_url + "safsmsverify"
safe_login_quick_url = base_url + "safloginquick"
member_profile_url = base_url + "memprofile"
upload_par_url = base_url + "uploadpar"
upload_file_url = base_url + "uploadfile"
task_state_url = base_url + "taskstate"
task_down_url = base_url + "taskdown"

# 普通请求头
okhttp_headers = {
    'Host': host,
    'User-Agent': 'okhttp/3.14.9'
}

# 上传文件请求头
upload_headers = {
    'Content-Type': 'application/octet-stream',
    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 8; Mi 20 Build/QQ3A.200805.001)',
    'Host': host
}


class TaskInfo:
    """
    任务信息
    """

    def __init__(self, task_tag, task_token, timestamp, filename):
        self.task_tag = task_tag
        self.task_token = task_token
        self.timestamp = timestamp
        self.filename = filename


# 计算datasign字段
def calculate_data_sign(data_dict):
    # 按键升序排列
    sorted_tuple = sorted(data_dict.items(), key=lambda d: d[0], reverse=False)
    content = ''
    for t in sorted_tuple:
        content += '&{}={}'.format(t[0], t[1])
    content += 'hUuPd20171206LuOnD'
    if content.startswith("&"):
        content = content.replace("&", "", 1)
    md = hashlib.md5()
    md.update(content.encode('utf-8'))
    return md.hexdigest()


def post_request_normal(url, add_headers_dict=None, need_user_token=True, custom_headers=None):
    data = custom_headers if custom_headers else {
        "deviceid": device_id,
        "timestamp": int(time.time()),
        "productinfo": product_info,
        "account": account,
    }
    if add_headers_dict:
        for key, value in add_headers_dict.items():
            data[key] = value
    if need_user_token:
        data['usertoken'] = user_token
    data['datasign'] = calculate_data_sign(data)
    resp = requests.post(url=url, headers=okhttp_headers, data=data)
    logger.info("请求：{}".format(resp.url))
    logger.info("参数：{}".format(data))
    if resp:
        try:
            resp_json = resp.json()
            logger.info("响应：{}".format(resp_json))
            return resp_json
        except Exception as e:
            logger.error("json解析异常：{}".format(e))
            return None
    else:
        exit("接口请求异常...")


# 检查Token是否可用
def check_token():
    resp_json = post_request_normal(check_token_url, None)
    if resp_json:
        if resp_json['code'] == 10000:
            logger.info("校验Token完毕：处于登录状态...")
            return True
        else:
            logger.info("校验Token失败，需要重新登录...")
            if safe_sms_verify():
                verification_code = input("请输入验证码：")
                return safe_login_quick(verification_code)
            return False
    else:
        exit("校验Token接口异常")


# 发送验证码
def safe_sms_verify():
    resp_json = post_request_normal(safe_sms_verify_url, {'verifytype': 'quicklogin'}, False)
    if resp_json:
        if resp_json['code'] == 10000:
            logger.info("验证码发送成功...：{}".format(resp_json))
            return True
        else:
            return False
    else:
        exit("获取验证码接口异常")


# 调用登录接口
def safe_login_quick(sms_code):
    global user_token
    resp_json = post_request_normal(safe_login_quick_url, {'smscode': sms_code, 'showvip': 1}, False)
    if resp_json:
        if resp_json['code'] == 10000:
            logger.info("登录成功...")
            user_token = resp_json['userinfo']['usertoken']
            update_configs('xj-api', {'user_token': user_token})
            logger.info("刷新配置文件中的 usertoken成功...")
            return True
        else:
            return False
    else:
        exit("接口请求异常...")


# 文件上传校验
def upload_par(file_path):
    logger.info("建立文件上传任务：{}".format(file_path))
    file_name = file_path.split(os.path.sep)[-1]
    resp_json = post_request_normal(upload_par_url, None, need_user_token=False, custom_headers={
        "outputfileextension": "srt",
        "tasktype": "voice2text",
        "productid": "34",
        "isshare": 0,
        "softname": software_name,
        "usertoken": user_token,
        "filecount": 1,
        "filename": file_name,
        "machineid": device_id,
        "fileversion": "defaultengine",
        "softversion": "7.0.0",
        "fanyi_from": "ZH",
        "limitsize": "204800",
        "parainfo": "convertcore:Duiai",  # 可选模型：Ali、Duiai
        "account": account,
        "timestamp": int(time.time())
    })
    if resp_json:
        if resp_json['code'] == 10000:
            logger.info("文件上传任务已建立，开始执行分块上传...")
            return upload_file(
                TaskInfo(resp_json['tasktag'], resp_json['tasktoken'], resp_json['timestamp'], file_name),
                file_path)
    else:
        return None


# 文件分块上传
def upload_file(upload_task, file_path):
    # 获得文件字节数
    file_size = os.path.getsize(file_path)
    # 计算文件块数
    chunks_count = math.ceil(file_size / 1048576)
    upload_params = {
        'tasktag': upload_task.task_tag,
        'timestamp': upload_task.timestamp,
        'tasktoken': upload_task.task_token,
        'fileindex': 0,
        'chunks': chunks_count,
    }
    # 分段请求
    for count in range(chunks_count):
        upload_params['chunk'] = count
        start_index = count * 1048576
        with open(file_path, 'rb') as f:
            f.seek(start_index)
            content = f.read(1048576)
            resp = requests.post(url=upload_file_url, headers=upload_headers, params=upload_params, data=content)
            logger.info("请求：{}".format(resp.url))
            if resp is not None:
                logger.info("{}".format(resp.json()))
            count += 1
    return upload_task


# 查询任务执行状态
def task_state(upload_task):
    count = 1
    while True:
        resp_json = post_request_normal(task_state_url, None, False, custom_headers={
            "ifshowtxt": "1",
            "productid": "34",
            "deviceos": "android10",
            "softversion": "4.3.2",
            "tasktag": upload_task.task_tag,
            "softname": software_name,
            "usertoken": user_token,
            "deviceid": device_id,
            "devicetype": "android",
            "account": account,
            "timestamp": int(time.time())
        })
        if resp_json:
            if resp_json['code'] == 10000:
                return True
            elif resp_json['code'] == 20000:
                time.sleep(10 if count > 11 else count)
                count += 1
                continue
            elif resp_json['code'] == 18000:
                logger.info("任务处理失败，请稍后重试 → 【{} → {}】".format(upload_task.task_tag, upload_task.filename))
                break
        else:
            logger.error("查询任务执行状态失败...")
            return False


# 获取字幕提取结果
def task_down(upload_task, output_file_prefix):
    resp_json = post_request_normal(task_down_url, {
        "downtype": 2,
        "tasktag": upload_task.task_tag,
    })
    if resp_json:
        download_url = resp_json.get('downurl')
        logger.info("字幕文件地址：{}".format(download_url))
        if download_url is not None:
            download_resp = requests.get(download_url)
            if download_resp is not None:
                file_name = os.path.join(srt_save_dir, "{}.srt".format(output_file_prefix))
                with open(file_name, 'wb') as f:
                    f.write(download_resp.content)
                    logger.info("SRT格式字幕文件保存成功：{}".format(file_name))
                    return file_name


# 解析srt文件提取时间及内容列表
def analyse_srt(srt_file_path):
    time_list = []
    text_list = []
    time_start_pos = 1
    text_start_pos = 2
    with open(srt_file_path, 'rb') as f:
        for i, value in enumerate(f.readlines()):
            if i == time_start_pos:
                time_list.append(value.decode().strip()[0:8])
                time_start_pos += 4
            elif i == text_start_pos:
                text_list.append(value.decode().strip())
                text_start_pos += 4
    return time_list, text_list


# 转换为txt格式的字幕文件
def save_subtitle(file_name, text_list):
    file_path = os.path.join(txt_save_dir, "{}.txt".format(file_name))
    write_text_list_to_file(text_list, file_path)
    logger.info("TXT格式字幕文件保存成功：{}".format(file_path))
    return file_path


# 视频转mp3
def video_to_mp3(input_file, output_file_prefix):
    output_file = os.path.join(mp3_save_dir, "{}.mp3".format(output_file_prefix))
    os.system("ffmpeg -i {} -f mp3 -acodec libmp3lame -y {}".format(input_file, output_file))
    return output_file


if __name__ == '__main__':
    is_dir_existed(xj_input_dir)
    is_dir_existed(mp3_save_dir)
    is_dir_existed(srt_save_dir)
    is_dir_existed(txt_save_dir)
    video_file_list = search_all_file(xj_input_dir, ('.flv', '.mp4', '.ts', '.m4a', ".mp3", ".wav"))
    if len(video_file_list) == 0:
        logger.info("未在此目录下发现视频文件：{}".format(xj_input_dir))
        exit(0)
    else:
        logger.info("检索到当前目录下的视频文件有这些：")
        logger.info("=" * 64)
        for pos, video_path in enumerate(video_file_list):
            logger.info("{} → {}".format(pos, video_path))
        logger.info("=" * 64)
        choose_input = input("请输入要提取字幕的音视频序号回车，如果要转换全部视频直接回车：")
        file_choose_index = -1
        if len(choose_input) > 0:
            file_choose_index = int(choose_input)
            if file_choose_index >= len(video_file_list):
                exit("数组下标越界")
        need_handle_video_list = \
            video_file_list if file_choose_index == -1 else video_file_list[file_choose_index: file_choose_index + 1]
        txt_output_file_list = []
        for pos, video_file in enumerate(need_handle_video_list):
            logger.info("正在处理【{}/{}】个视频...".format(pos + 1, len(need_handle_video_list)))
            file_name_prefix = os.path.splitext(os.path.basename(video_file))[0]
            mp3_file = video_to_mp3(video_file, file_name_prefix)
            task = upload_par(mp3_file)
            if task:
                if task_state(task):
                    srt_path = task_down(task, file_name_prefix)
                    txt_output_file_list.append(save_subtitle(file_name_prefix, analyse_srt(srt_path)[1]))
        logger.info("所有字幕提取完毕，输出文件如下：")
        for txt_output_file in txt_output_file_list:
            logger.info(txt_output_file)
