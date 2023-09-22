# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : generate_mock_data.py
   Author   : CoderPig
   date     : 2023-07-11 14:43
   Desc     : 根据 Kotlin实体类代码 生成用于Mock的Response Data数据
   使用方法  : 把Kotlin实体类的代码贴到【Kotlin实体类.txt】文件中，引用到的类型也要包含
              然后直接生成json数据，json解析异常一般是漏了引用到的实体类，或者没有继承Serializable接口
-------------------------------------------------
"""
import json
import random
import re
import time
from collections import OrderedDict

from util.file_util import read_file_text_content, if_file_existed, write_text_to_file

data_type_pattern = re.compile(r"data class (.*?)\((.*?)\) ?: Serializable( {.*?})?", re.DOTALL)  # 提取数据类的正则
field_match_pattern = re.compile(r"va[rl] ?(\w+): ?([\w<>?]+)", re.S)  # 提取成员属性的正则
list_data_type_pattern = re.compile(r".*?List<(.*?)\?*>", re.S)  # 列表泛型具体类型提取的正则
response_json_template = '{ "code":200, "msg":"成功", "data":{%s}}'  # 响应Json模板

kotlin_entity_class_file = "Kotlin实体类.txt"  # Kotlin实体类代码，需要包含引用到的类型，否则会导致生成的json异常
mock_response_json_file = "Mock用的Json.txt"  # 生成mock数据的文件


class Field:
    def __init__(self):
        self.name = None
        self.data_type = None
        self.value = None


class DataType:
    def __init__(self, class_name=None):
        self.class_name = class_name  # 类型类名
        self.field_list = []  # 该类型的属性

    def show_fields(self):
        result = ""
        for f in self.field_list:
            result += "{} → {}".format(f.name, f.data_type)
        return result


def traverse_fields_to_json(data_type):
    global data_json
    for field in data_type.field_list:
        if field.data_type.find("List") != -1:
            data_json += '"{}":'.format(field.name)
            data_json += '['
            list_data_type_result = list_data_type_pattern.search(field.data_type)
            if list_data_type_result:
                list_data_type_str = list_data_type_result.group(1)
                list_data_type = data_type_dict.get(list_data_type_str)
                if list_data_type:
                    data_json += '{'
                    traverse_fields_to_json(list_data_type)
                    data_json += '}'
                else:
                    if list_data_type_str == "Int" or list_data_type_str == "Long":
                        data_json += "1"
                    elif list_data_type_str == "Float" or list_data_type_str == "Double" \
                            or list_data_type_str == "BigDecimal":
                        data_json += "88.88"
                    elif list_data_type_str == "Boolean":
                        data_json += True
                    else:
                        data_json += list_data_type_str
            else:
                data_json += "None"
            data_json += "],"
        else:
            sub_data_type = data_type_dict.get(field.data_type)
            if sub_data_type:
                # 字段有子类型
                data_json += '"%s":{' % field.name
                traverse_fields_to_json(sub_data_type)
                data_json += "},"
            else:
                data_json += '"{}":{},'.format(field.name, field.value)


def generate_mock_response_json():
    global data_type_dict
    for data_type in data_type_result:
        field_result = field_match_pattern.findall(data_type[1].replace("\n", ""))
        if len(data_type[2]) > 0:
            field_result += field_match_pattern.findall(data_type[2].replace("\n", ""))
        temp_data_type = DataType(data_type[0])
        for field in field_result:
            temp_field = Field()
            temp_field.name = field[0].strip()
            temp_field.data_type = field[1].strip().replace("?", "")
            if temp_field.data_type == "Int":
                temp_field.value = 1
            elif temp_field.data_type == "BigDecimal":
                temp_field.value = 88888888.88
            elif temp_field.name.lower().find("time") != -1 or temp_field.name.lower().find("date") != -1:
                temp_field.value = str(round(time.time() * 1000))
            elif temp_field.name.lower().find("url") != -1:
                temp_field.value = '"https://img.cdn.xxx.com/image/2023/06/27/281a405c-2870-4f36-85e4' \
                                   '-4363b0a287b9/d725c3a9-f5f2-4a82-a9a1-77eb5ebfbeaf.png"'
            elif temp_field.name.lower().endswith("id") or temp_field.data_type == "Long":
                temp_field.value = int(''.join(random.choice('0123456789') for _ in range(19)))
            elif temp_field.data_type == "String":
                temp_field.value = '"字符串"'
            elif temp_field.data_type == "Boolean":
                temp_field.value = "true"
            elif temp_field.data_type == "Double" or temp_field.data_type == "Float":
                temp_field.value = 66.66
            temp_data_type.field_list.append(temp_field)
        data_type_dict[data_type[0]] = temp_data_type
    # 最顶层的数据类型
    traverse_fields_to_json(list(data_type_dict.values())[0])
    json_result = (response_json_template % data_json).replace(',}', '}')
    try:
        mock_response_json = json.dumps(json.loads(json_result), indent=4, ensure_ascii=False)
        write_text_to_file(mock_response_json, mock_response_json_file)
    except json.decoder.JSONDecodeError:
        exit("Json解析异常，请检查是否漏掉了需要用到的Entity累哦：\n{}".format(json_result))


if __name__ == '__main__':
    data_type_dict = OrderedDict()
    if not if_file_existed(kotlin_entity_class_file):
        open(kotlin_entity_class_file, "w").close()
    data_type_result = data_type_pattern.findall(read_file_text_content(kotlin_entity_class_file))
    if data_type_result:
        data_json = ""
        generate_mock_response_json()
    else:
        exit("实体类解析异常....")
