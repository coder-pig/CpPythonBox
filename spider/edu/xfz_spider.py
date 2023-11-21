# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : xfz_spider.py
   Author   : CoderPig
   date     : 2023-11-20 15:04
   Desc     : 某小自考站点的题库爬取
-------------------------------------------------
"""
import time

import requests as r
import re
import os
from lxml import etree

from util.file_util import write_text_list_to_file, read_list_from_file

requests_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Cookie': 'xxx',
    'Host': 'xfz.5zk.com.cn'
}

base_url = 'https://xfz.5zk.com.cn/zk8exam/'

chapter_exercise_url = base_url + "studycenter_zy.php"  # 章节URL
chapter_practice_url = base_url + "wiki_exam_zy.php?TypeId={}&jjwikiid={}"  # 练习
repeat_learning_url = base_url + "apply_cx_zy.action.php?&jjwikiid={}"  # 申请重学

tm_url = "https://xfz.5zk.com.cn/zk8exam/wiki_exam_zy.php?TypeId={}&jjwikiid={}&chapterid={}&n_or_p=2&yuan_ct_Id={}"  # 练习

gotozy_pattern = re.compile(r'gotozy\((\d+),(\d+)\)', re.S)
next_url_pattern = re.compile(r'(wiki_exam_zy\.php.*?)"', re.S)
answer_pattern = re.compile(r'正确答案：.*?/>(.*?)</', re.S)
type_id_to_wiki_id_list = os.path.join(os.getcwd(), 'id_list.txt')
result_txt = os.path.join(os.getcwd(), 'result.txt')
data_list = []
question_set = set()


# 拉取章节id保存到本地
def fetch_chapter():
    resp = r.get(chapter_exercise_url, headers=requests_header)
    if resp:
        result_list = []
        for result in gotozy_pattern.findall(resp.text):
            result_list.append("{}\t{}".format(result[0], result[1]))
        write_text_list_to_file(result_list, type_id_to_wiki_id_list)


# 拉取章节练习
def fetch_chapter_exercise(type_id, wiki_id):
    empty_count = 6
    while True:
        try:
            if empty_count == 0:
                break
            request_url = chapter_practice_url.format(type_id, wiki_id)
            print("请求的url：", request_url)
            resp = r.get(request_url, headers=requests_header)
            data, next_url = fetch_data(resp)
            if data.question not in question_set:
                question_set.add(data.question)
                data_list.append(data.to_str())
            for i in range(4):
                request_url = base_url + next_url
                print("请求的url：", request_url)
                next_resp = r.get(request_url, headers=requests_header)
                data, next_url = fetch_data(next_resp)
                if data.question not in question_set:
                    question_set.add(data.question)
                    data_list.append(data.to_str())
                time.sleep(5)
            if len(data_list) == 0:
                empty_count -= 1
            else:
                write_text_list_to_file(data_list, result_txt, "a+")
                data_list.clear()
            resp = r.get(repeat_learning_url.format(wiki_id), headers=requests_header)
            print("请求的url：", resp.url)
        except Exception as e:
            print(e)
            continue


def fetch_data(resp):
    selector = etree.HTML(resp.text)
    title = selector.xpath('//h3[@class="block-title"]')[0].text
    title_split_list = title.split(" ")
    option_str = ''
    question = selector.xpath("//div[@class='form-material-success']")[2].text
    if "案例分析" in question or "简答" in question or "名词解释" in question:
        answer = answer_pattern.search(resp.text).group(1)
    else:
        answer = selector.xpath("//input[@id='tright']")[0].attrib.get('value')
        option_list = selector.xpath('//span[@class="css-control-indicator"]')
        for option in option_list:
            option_str += option.tail.replace("\t", "").lstrip() + '$'
    return Data(title_split_list[0], title_split_list[1], question, answer, option_str), next_url_pattern.search(
        resp.text).group(1)


def fetch_tm(type_id, wiki_id, chapter_id, yuan_ct_id):
    resp = r.get(tm_url.format(type_id, wiki_id, chapter_id, yuan_ct_id), headers=requests_header)
    print(resp.text)


class Data:
    def __init__(self, article=None, subject=None, question=None, answer=None, options=None):
        self.article = article
        self.subject = subject
        self.question = question
        self.answer = answer
        self.options = options

    def to_str(self):
        return "{}\t{}\t{}\t{}\t{}".format(self.article, self.subject, self.question, self.answer, self.options)


if __name__ == '__main__':
    # 拉取章节id
    # fetch_chapter()
    # 遍历拉取所有章节
    ids_list = read_list_from_file(type_id_to_wiki_id_list)
    for ids in ids_list:
        id_split_list = ids.split("\t")
        if len(id_split_list) > 0:
            fetch_chapter_exercise(id_split_list[0], id_split_list[1])
