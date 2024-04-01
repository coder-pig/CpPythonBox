# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : zp_test.py
   Author   : CoderPig
   date     : 2024-03-15 17:20
   Desc     : 
-------------------------------------------------
"""
import json
import time

import requests
import jwt
from util.file_util import read_file_text_content


def generate_token(apikey: str, exp_seconds: int):
    try:
        tid, secret = apikey.split(".")
    except Exception as e:
        raise Exception("invalid apikey", e)

    payload = {
        "api_key": tid,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }

    result = jwt.encode(
        payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )
    return result


if __name__ == '__main__':
    data = {
        "model": "glm-3-turbo",
        "stream": False,
        "messages": [
            {
                "role": "user",
                "content": "基于以下文章摘要列表，请你分析并生成一个尽可能详细的作者画像。请考虑作者的写作风格、专业知识领域、价值观和态度等方面。{}".format(
                    read_file_text_content("test.txt"))
            }
        ]
    }
    resp = requests.post("https://open.bigmodel.cn/api/paas/v4/chat/completions", headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + generate_token("xxx.xxx", 60)
    }, data=json.dumps(data))
    print(json.dumps(data))
    print(resp.text)
