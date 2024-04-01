# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : apifox.py
   Author   : CoderPig
   date     : 2024-02-29 15:46
   Desc     : 动态更新apifox的接口返回数据
-------------------------------------------------
"""
import json

import requests as r

headers = {
    'X-Apifox-Version': '2024-01-20',
    'Authorization': 'Bearer APS-xxx',
    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
    'Content-Type': 'application/json'
}


def get_api_info(project_id, api_id):
    request_url = "https://api.apifox.com/api/v1/projects/{}/http-apis/{}?locale=zh-CN".format(project_id, api_id)
    resp = r.get(request_url, headers=headers)
    print(resp.url)
    data_json = resp.json()['data']
    print(resp.text)
    # 对下不变的参数
    put_data = {
        "tags": data_json['tags'],
        "requestBody": data_json['requestBody'],
        "parameters": data_json['parameters'],
        "name": data_json['name'],
        "description": "还是得会返回",
        "method": data_json['method'],
        "path": data_json['path'],
        "status": data_json['status'],
        "projectId": data_json['projectId'],
        "folderId": data_json['folderId'],
        "auth": data_json['auth'],
        "advancedSettings": data_json['advancedSettings'],
        "responseChildren": data_json['responseChildren'],
    }
    # response字段结构层级不一样，要单独处理下
    origin_response = data_json['responses'][0]
    response_dict = {
        "apiDetailId": origin_response['apiDetailId'],
        "code": origin_response['code'],
        "contentType": origin_response['contentType'],
        "defaultEnable": origin_response['defaultEnable'],
        "jsonSchema": origin_response['jsonSchema'],
        "name": origin_response['name'],
    }
    # 请求聚合数据的新闻头条数据
    juhe_resp = r.get("https://v.juhe.cn/toutiao/index", params={"key": "xxx"})
    juhe_json = juhe_resp.text
    print(juhe_json)
    # 只覆盖第一页
    response_dict['responseExamples'] = [juhe_json]
    put_data['responses'] = response_dict
    # 调用修改接口修改返回数据
    print(json.dumps(put_data))
    resp = r.put(request_url, headers=headers, json=put_data)
    print(resp.text)


if __name__ == '__main__':
    get_api_info(4081539, 151093222)
