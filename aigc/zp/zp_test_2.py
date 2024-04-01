# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : zp_test.py
   Author   : CoderPig
   date     : 2024-03-15 17:20
   Desc     : 智谱AI调用示例
-------------------------------------------------
"""
import base64
import hashlib
import hmac
import json
import time

import requests

from util.file_util import read_file_text_content


# 生成鉴权Token
def generate_token(apikey: str, exp_seconds: int):
    try:
        kid, secret = apikey.split(".")
    except Exception as e:
        raise Exception("invalid apikey", e)

    # Header
    header = {
        "alg": "HS256",
        "sign_type": "SIGN"
    }

    # Payload
    payload = {
        "api_key": kid,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }

    # Encode Header
    header_encoded = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')

    # Encode Payload
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')

    # Create Signature
    to_sign = f'{header_encoded}.{payload_encoded}'.encode()
    signature = hmac.new(secret.encode(), to_sign, hashlib.sha256)
    signature_encoded = base64.urlsafe_b64encode(signature.digest()).decode().rstrip('=')

    # Create JWT
    jwt_token = f'{header_encoded}.{payload_encoded}.{signature_encoded}'

    return jwt_token


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
