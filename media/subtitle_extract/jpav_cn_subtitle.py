# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : jpav_cn_subtitle.py
   Author   : CoderPig
   date     : 2023-10-20 9:53
   Desc     : 艾薇中文字幕生成
-------------------------------------------------
"""
import math

import ffmpeg
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# from transformers import pipeline
import openai

from config_getter import get_config
from util.file_util import read_file_text_content, read_list_from_file

# 定义输入和输出文件路径
input_file = 'test.mp4'
output_file = 'output.wav'


# ffmpeg提取视频中的音频

def fetch_audio_from_video(video_path, audio_path):
    ffmpeg.input(filename=video_path).output(audio_path, af="pan=1c|c0=c1", ac="1", acodec='pcm_s16le', f='wav').run()


def translate_by_openai(content):
    openai.api_key = get_config('openai_token', 'openai')
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt="你是一个专业的翻译工作者，请将下面这段日文的段落翻译成中文：{}".format(content),
        temperature=1,
        max_tokens=2000,
        frequency_penalty=0,
        presence_penalty=0
    )
    print(response["choices"][0]["text"].strip())


if __name__ == '__main__':
    # ja_en_model_path = r"E:\Code\HuggingFace\ja-en"
    # ja_en_tokenizer = AutoTokenizer.from_pretrained(ja_en_model_path)
    # ja_en_model = AutoModelForSeq2SeqLM.from_pretrained(ja_en_model_path)
    # ja_en_pipeline = pipeline("translation", model=ja_en_model, tokenizer=ja_en_tokenizer)
    #
    # en_cn_model_path = r"E:\Code\HuggingFace\en-zh"
    # en_cn_tokenizer = AutoTokenizer.from_pretrained(en_cn_model_path)
    # en_cn_model = AutoModelForSeq2SeqLM.from_pretrained(en_cn_model_path)
    # en_cn_pipeline = pipeline("translation", model=en_cn_model, tokenizer=en_cn_tokenizer)

    # translation_content_list = read_list_from_file("short.txt")
    # for translation_content in translation_content_list:
    # en_result = ja_en_pipeline(translation_content)
    # zh_result = en_cn_pipeline(en_result[0]['translation_text'])
    # print("{} === {}".format(en_result[0]['translation_text'], zh_result[0]['translation_text']))
    # translate_by_openai(translation_content)
    translation_content = read_file_text_content("short.txt").replace("\n", ",")
    translate_by_openai(translation_content)
