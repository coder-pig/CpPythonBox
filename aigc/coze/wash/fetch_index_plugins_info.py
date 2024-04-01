# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : fetch_index_plugins_info.py
   Author   : CoderPig
   date     : 2024-02-22 14:07
   Desc     : 
-------------------------------------------------
"""
import json
import os

from util.file_util import read_file_text_content, search_all_file, write_text_to_file


def fetch_index_plugins_info():
    json_file = 'coze_index_plugins.json'
    plugins = json.loads(read_file_text_content(json_file))['data']['products']
    result_str = "|**插件工具名**|**所属插件**|**工具作用**|\n|:----|:----|:----|\n"
    for plugin in plugins:
        meta_info = plugin['meta_info']
        for tool in plugin['plugin_extra']['tools']:
            result_str += "|**{}**|{}|{}|\n".format(tool['name'], meta_info['name'],
                                                    tool['description'].replace("\n", "\t"))
    print(result_str)


def fetch_bot_ids_list():
    json_file = 'coze_index_bots_info.json'
    bots = json.loads(read_file_text_content(json_file))['data']['bot_draft_list']
    result_str = "const botInfoArray = ["
    for bot in bots:
        result_str += '"{}-{}",'.format(bot['id'], bot['name'])
    print(result_str[:-1] + "]")


def filter_workflow_id_list():
    # 读取所有Json文件
    result_str = "const workflowInfoArray = ["
    json_file_list = search_all_file(os.path.join(os.getcwd(), "bot_detail"), ".json")
    for json_file in json_file_list:
        data = json.loads(read_file_text_content(json_file))['data']
        workflow_list = json.loads(data['work_info']['workflow'])
        # 只输出有工作流的Bot
        if len(workflow_list) > 0:
            # 遍历工作流列表 (看下有哪些Bot有多个工作流)
            for workflow in workflow_list:
                # print("【{}】{}".format(data['name'], workflow))
                result_str += '"{}-{}-{}",'.format(data['name'], workflow['name'], workflow['workflow_id'])
    print(result_str[:-1] + "]")


def filter_workflow_plugin_list():
    # 读取所有Json文件
    json_file_list = search_all_file(os.path.join(os.getcwd(), "workflow_detail"), ".json")
    for json_file in json_file_list:
        schema = json.loads(json.loads(read_file_text_content(json_file))['data']['workflow']['schema_json'])
        for node in schema['nodes']:
            # 过滤插件节点，输出子标题
            if node['type'] == "3":
                print("【{}】 → {}".format(json_file.split(os.path.sep)[-1].replace(".json", ""),
                                         node['data']['inputs']['llmParam']))


def generate_prompts_md():
    json_file_list = search_all_file(os.path.join(os.getcwd(), "bot_detail"), ".json")
    md_content = "# Coze(扣子)-官方Bots提示词汇总\n"
    for json_file in json_file_list:
        data = json.loads(read_file_text_content(json_file))['data']
        md_content += "\n## {}\n\n".format(data['name'])
        prompt_list = json.loads(data['work_info']['system_info_all'])
        md_content += '```\n{}\n```\n---\n'.format(prompt_list[0]['data'])
    write_text_to_file(md_content, "coze_bots_prompts.md")


if __name__ == '__main__':
    # fetch_index_plugins_info()
    # fetch_bot_ids_list()
    # filter_workflow_id_list()
    # filter_workflow_plugin_list()
    generate_prompts_md()
