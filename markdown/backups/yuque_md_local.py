# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : yuque_md_local.py
   Author   : CoderPig
   date     : 2023-10-30 16:37
   Desc     : 语雀备份脚本
-------------------------------------------------
"""
import asyncio
import os

from backups_util import md_to_local
from util.file_util import is_dir_existed, search_all_file, write_text_to_file
from openpyxl import load_workbook
from util.logger_util import default_logger
import re
import requests as r
import time
from random import randint

logger = default_logger()
output_dir = os.path.join(os.getcwd(), "output{}{}".format(os.sep, "yuque"))
origin_md_dir = os.path.join(output_dir, "origin_md")  # 生成的原始md文件
local_md_dir = os.path.join(output_dir, "local_md")  # 生成的本地md文件
yq_base_url = "https://www.yuque.com/api/v2/{}"

pic_match_pattern = re.compile(r'(!\[.*?\]\()(.*?)(\.(png|PNG|jpg|JPG|jepg|gif|GIF|svg|SVG|webp|awebp))(.*?)\)', re.M)

yq_headers = None
doc_count = 0


def pic_url_func(result):
    """
    从正则匹配结果提取图片URL的方法
    :param result: 正则匹配结果
    :return: 图片URL
    """
    return result[2] + result[3] + result[5]


def pic_suffix_func(result):
    """
    从正则匹配结果提取图片后缀的方法
    :param result: 正则匹配结果
    :return: 图片后缀
    """
    return result[4]


def replace_result_func(result, relative_path):
    """
    返回替换后的字符串
    :param result: 正则匹配结果
    :param relative_path: 图片的相对路径
    :return:
    """
    return "{}{}{}".format(result[1], relative_path, ")")


# 知识库
class Repo:
    def __init__(self, repo_id, repo_type, repo_slug, repo_name, repo_namespace):
        self.repo_id = repo_id
        self.repo_ype = repo_type
        self.repo_slug = repo_slug
        self.repo_name = repo_name
        self.repo_namespace = repo_namespace


# 目录结点
class TocNode:
    def __init__(self, node_type, node_title, node_uuid, parent_uuid, doc_id, repo_id, repo_name):
        self.node_type = node_type
        self.node_title = node_title
        self.node_uuid = node_uuid
        self.parent_uuid = parent_uuid
        self.child_node_list = []
        self.doc_id = doc_id
        self.repo_id = repo_id
        self.repo_name = repo_name


# 文档
class Doc:
    def __init__(self, doc_id, book_id, book_name, doc_slug, doc_title, doc_content):
        self.doc_id = doc_id
        self.book_id = book_id
        self.book_name = book_name;
        self.doc_slug = doc_slug
        self.doc_title = doc_title
        self.doc_content = doc_content

    def save_to_md(self):
        save_path = "{}{}{}{}{}.md".format(origin_md_dir, os.path.sep, self.book_name, os.path.sep,
                                           self.doc_title)
        logger.info(save_path)


def send_request(desc, api):
    """
    请求通用封装
    :param desc:
    :param api:
    :return:
    """
    request_url = yq_base_url.format(api)
    logger.info("请求{}接口：{}".format(desc, request_url))
    return r.get(request_url, headers=yq_headers)


def fetch_user_id():
    """
    获取语雀用户id
    :return:语雀用户id
    """
    # 获取用户ID
    user_resp = send_request("获取用户ID", "user")
    user_id = None
    if user_resp:
        user_id = user_resp.json().get('data').get('id')
        logger.info("当前用户ID：{}".format(user_id))
    if user_id is None:
        exit("用户ID获取失败，请检查后重试...")
    return user_id


def fetch_repo_list():
    """
    拉取知识库列表
    :return:
    """
    repo_list_resp = send_request("知识库列表", "users/{}/repos".format(yq_user_id))
    repo_list = []
    if repo_list_resp:
        repo_list_json = repo_list_resp.json()
        for repo in repo_list_json['data']:
            repo_list.append(
                Repo(repo.get('id'), repo.get('type'), repo.get('slug'), repo.get('name'), repo.get('namespace')))
    if len(repo_list) == 0:
        exit("知识库列表获取失败，请检查后重试...")
    else:
        logger.info("解析知识库列表成功，共{}个知识库...".format(len(repo_list)))
    logger.info("=" * 64)
    return repo_list


def fetch_toc_list(repo_id, repo_name):
    """
    拉取知识库目录
    :param repo_id: 知识库id
    :param repo_name: 知识库名称
    :return:
    """
    toc_list_resp = send_request("目录列表", "repos/{}/toc".format(repo_id))
    id_order_dict = {}
    root_toc_node = TocNode(None, "根目录", None, None, None, repo_id, repo_name)
    id_order_dict["root"] = root_toc_node
    if toc_list_resp:
        toc_list_json = toc_list_resp.json()
        for toc in toc_list_json['data']:
            toc_node = TocNode(toc.get('type'), toc.get('title'), toc.get('uuid'), toc.get('parent_uuid'),
                               toc.get('doc_id'), repo_id, repo_name)
            id_order_dict[toc_node.node_uuid] = toc_node
            # 顶级目录
            if toc_node.parent_uuid is None or len(toc_node.parent_uuid) == 0:
                root_toc_node.child_node_list.append(toc_node)
            else:
                parent_node = id_order_dict.get(toc_node.parent_uuid)
                if parent_node is None:
                    exit("父目录不存在")
                else:
                    parent_node.child_node_list.append(toc_node)
    for node in root_toc_node.child_node_list:
        traverse_nodes(node)


def traverse_nodes(node, save_path=""):
    """
    递归遍历目录结点的方法
    :param node:    当前结点
    :param save_path:   文件的保存路径
    :return:
    """
    save_path += "{}{}".format(os.sep, node.node_title)
    if node.child_node_list is None or len(node.child_node_list) == 0:
        if node.node_type == "DOC":
            format_repo_name = node.repo_name.replace("|", "_").replace("/", "、").replace('"', "'").replace(":", "；")
            format_save_path = save_path.replace("|", "_").replace("/", "、").replace('"', "'").replace(":", "；")
            md_save_path = "{}{}{}{}.md".format(origin_md_dir, os.sep, format_repo_name, format_save_path)
            last_sep_index = md_save_path.rfind(os.sep)
            if last_sep_index != -1:
                save_dir = md_save_path[:last_sep_index]
                is_dir_existed(save_dir)
                fetch_doc_detail(node, md_save_path)
        return
    else:
        for node in node.child_node_list:
            traverse_nodes(node, save_path)


# 拉取单篇文章的详细内容
def fetch_doc_detail(node, save_path):
    global doc_count
    doc_detail_resp = send_request("文档详情", "repos/{}/docs/{}".format(node.repo_id, node.doc_id))
    if doc_detail_resp:
        doc_detail_json = doc_detail_resp.json()
        doc_detail = doc_detail_json.get('data').get('body')
        if doc_detail is not None and len(doc_detail) > 0:
            write_text_to_file(doc_detail, save_path)
            doc_count += 1
            logger.info("第【{}】篇文档备份成功...".format(doc_count))
            time.sleep(randint(0, 3))  # 随机休眠2-8s，细水长流~


if __name__ == '__main__':
    is_dir_existed(origin_md_dir)
    is_dir_existed(local_md_dir)
    yq_token = input("请输入你的语雀Token：")
    if len(yq_token) == 0:
        exit("请输入正确的Token！")
    yq_headers = {'X-Auth-Token': yq_token}
    logger.info("Token初始化成功...")
    logger.info("开始执行文档备份，请稍等...")
    yq_user_id = fetch_user_id()
    yq_repo_list = fetch_repo_list()
    for yq_repo in yq_repo_list:
        logger.info("开始拉取【{}】仓库下的文档".format(yq_repo.repo_name))
        fetch_toc_list(yq_repo.repo_id, yq_repo.repo_name)
    logger.info("文档备份完毕，开始执行Markdown文件批量本地化...")
    yq_doc_file_list = search_all_file(origin_md_dir, "md")
    logger.info("共扫描到Markdown文件【{}】篇，开始批量本地化...".format(len(yq_doc_file_list)))
    loop = asyncio.get_event_loop()
    md_to_local(origin_md_dir, local_md_dir, pic_match_pattern, loop, pic_url_func, pic_suffix_func,
                replace_result_func)
