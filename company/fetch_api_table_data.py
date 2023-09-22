# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : fetch_api_table_data.py
   Author   : CoderPig
   date     : 2023-07-10 15:40
   Desc     : 提取接口Wiki里的表格参数，转换输出：var 字段名: 类型? = null,
-------------------------------------------------
"""
import requests as r
import time
import io
import os
from PIL import Image
import re
from threading import Thread

from util.file_util import read_list_from_file, write_text_to_file

base_url = "http://xxx.xxx.xxx.com/server/index.php?s=/api"
# 查询用户信息
userinfo_url = base_url + "/user/info"
# 创建验证码
create_captcha_url = base_url + "/common/createCaptcha"
# 展示验证码
show_captcha_url = base_url + "/common/showCaptcha&captcha_id={}&{}"
# 登录接口
login_url = base_url + "/user/loginByVerify"
# 接口页
api_info_url = base_url + "/page/info"

username = "xxx"
passwd = "xxx"
user_token = ""
user_token_file = "user_token.txt"
analyze_result_file = "analyze_result.txt"

# 匹配正则
api_url_pattern = re.compile(r"http://xxx\.xxx\.xxx\.com/web/#/1/(\d+)", re.S)
table_cell_pattern = re.compile(r"^\|(.*?)\|$", re.M)
field_name_pattern = re.compile(r"[a-zA-Z]+")


def check_login_status():
    userinfo_resp = r.post(userinfo_url, data={"user_token": user_token})
    if userinfo_resp.json().get('error_code') == 10102:
        print("尚未登录，执行登录逻辑")
        return False
    else:
        print("处于登录状态，用户信息：")
        print(userinfo_resp.json())
        return True


def auto_login():
    global user_token
    create_captcha_resp = r.post(create_captcha_url)
    print("创建登录验证码")
    captcha_id = create_captcha_resp.json().get('data').get('captcha_id')
    if captcha_id:
        show_captcha_resp = r.get(show_captcha_url.format(captcha_id, int(round(time.time() * 1000))))
        if show_captcha_resp:
            print("图片验证码获取成功")
            Thread(target=Image.open(io.BytesIO(show_captcha_resp.content)).show).start()
            captcha = input("请输入登录验证码，以回车结束：")
            if captcha:
                login_resp = r.post(login_url, data={"username": username, "password": passwd, "captcha": captcha,
                                                     "captcha_id": captcha_id})
                if login_resp:
                    user_token = login_resp.json().get('data').get('user_token')
                    if user_token:
                        with open(user_token_file, "w+") as f:
                            f.write(user_token)
                            return True
                    else:
                        print("自动登录失败，请检查后重试...")
                        return False
    else:
        exit("创建失败...")
    return False

# 解析接口
def analyze_api_url(api_url):
    match_result = api_url_pattern.match(api_url)
    output_content = ""
    if match_result:
        page_id = match_result.group(1)
        api_info_resp = r.post(api_info_url, data={'page_id': page_id, "user_token": user_token})
        output_content += ("{}\n当前请求url：{}\n".format("=" * 48, api_url))
        if api_info_resp:
            page_content = api_info_resp.json()['data']['page_content']
            table_cell_result = table_cell_pattern.findall(page_content)
            print_flag = 0
            if table_cell_result:
                for table_cell in table_cell_result:
                    if table_cell.startswith("参数名"):
                        print_flag = 2
                    elif table_cell.startswith(":-"):
                        if print_flag == 2:
                            print_flag -= 1
                            output_content += ("{}\n".format("=" * 48))
                    else:
                        if print_flag > 0:
                            field_split_list = [x for x in table_cell.replace(" ", "").replace("\t", "").split("|") if
                                                x != "是" and x != "否" and x != "否是" and x != "是否"
                                                and "字段不能同时为空" not in x]
                            if len(field_split_list) > 2 and field_split_list[1] != "类型" and len(
                                    field_split_list[1]) > 0 and len(field_split_list[2]) > 0 \
                                    and "参数名" not in field_split_list[0] \
                                    and field_name_pattern.match(field_split_list[0]) \
                                    and field_split_list[2] != "描述":
                                # 数据类型处理
                                data_type = field_split_list[1]
                                if data_type == "Date" or data_type == "date" or data_type == "时间戳" \
                                        or data_type == "datetime" or data_type.find("long") != -1 \
                                        or data_type == "Long" \
                                        or data_type == "否(非普通跟进必传)" or data_type == "否（栋座详情页面请求必填）" \
                                        or data_type == "否（房源详情页面请求必填）":
                                    data_type = "Long"
                                elif data_type.find("int") != -1 or data_type == "Integer" \
                                        or data_type == "Int" or data_type == "Interger" \
                                        or data_type == "Byte" or data_type == "byte" \
                                        or data_type == "Boolean" or data_type == "boolean" \
                                        or data_type == "bool" or data_type == "布尔" \
                                        or data_type == "number" or data_type == "currentPage" \
                                        or data_type == "pageRows" or data_type == "是(土地和协同产业招商需求传)" \
                                        or data_type == "否(写字楼需求必填)" or data_type == "是（二级代理需求）" \
                                        or data_type == "否（二级代理需求）":
                                    data_type = "Int"
                                elif data_type == "float" or data_type == "Float":
                                    data_type = "Float"
                                elif data_type == "BigDecimal" or data_type == "Decimal" \
                                        or data_type == "bigDecimal" or data_type.find("decimal") != -1 \
                                        or data_type == "Double" or data_type == "double" \
                                        or data_type == "Doblue":
                                    data_type = "BigDecimal"
                                elif data_type.find("String") != -1 or data_type == "string" \
                                        or data_type == "str" or data_type == "stirng" \
                                        or data_type.find("char") != -1 or data_type == "text" \
                                        or data_type == "Satring" or data_type == "Stirng" \
                                        or data_type == "Strin" \
                                        or data_type == "否(土地需求必填)" or data_type == "编辑（不用修改）新增（非必填）":
                                    data_type = "String"
                                elif data_type.startswith("List") or data_type.startswith("list") \
                                        or data_type.find("数组") != -1 or data_type == "list" \
                                        or data_type.find("列表") != -1 \
                                        or data_type.find("Array") != -1 or data_type == "arrary" \
                                        or data_type.find("array") != -1 or data_type == "集合" \
                                        or data_type == "Arr" or data_type == "arr" \
                                        or data_type == "否(带看、谈判跟进必传)":
                                    data_type = "ArrayList<Any>"
                                elif "对象" in data_type or data_type.find("Object") != -1 or data_type == "object" \
                                        or data_type == "obj" or data_type == "Obj" \
                                        or data_type == "map" or data_type == "Map" \
                                        or data_type == "Attach" or data_type == "自定义实体" \
                                        or data_type.find("object") != -1 or data_type == "LabelParamValueVO" \
                                        or data_type == "OperationBulletinProcessVO" or data_type == "分页数据":
                                    data_type = "Any"
                                else:
                                    raise Exception("未知数据类型：{}".format(field_split_list))
                                output_content += ("var {}: {}? = null,  // {}\n".format(field_split_list[0], data_type,
                                                                                         field_split_list[2]))
            print("解析结束，写入结果文件中 ({})...".format(analyze_result_file))
            write_text_to_file(output_content, analyze_result_file)
        else:
            exit("接口请求失败，请检查后重试")
    else:
        exit("接口url地址有问题，请检查后重试...")


# 批量验证所有接口
def test_analyze():
    api_info_list = read_list_from_file('all_page_info.txt')
    for api_info in api_info_list:
        analyze_api_url("http://xxx.xxx.xxx.com/web/#/1/{}".format(api_info.split("~")[0]))


if __name__ == '__main__':
    if os.path.exists(user_token_file):
        with open(user_token_file, "r") as f:
            user_token = f.read()
    is_login = check_login_status()
    if not is_login:
        is_login_success = auto_login()
    else:
        input_url = input("请输入要提取数据的接口地址：")
        if len(input_url) > 0:
            analyze_api_url(input_url)
