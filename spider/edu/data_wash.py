# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : data_wash.py
   Author   : CoderPig
   date     : 2023-11-20 21:52
   Desc     : 
-------------------------------------------------
"""
import os
import xlwt
from util.file_util import fetch_all_file_list, read_list_from_file, write_text_to_file
import time

result_txt = os.path.join(os.getcwd(), 'result.txt')


def to_xls():
    sum_count = 0
    workbook = xlwt.Workbook(encoding='utf-8')
    data_list = read_list_from_file(result_txt)
    count = 1
    lesson_name = None
    worksheet = None
    for data in data_list:
        data_split_list = data.split("\t")
        if lesson_name != data_split_list[0]:
            lesson_name = data_split_list[0]
            count = 1
            worksheet = workbook.add_sheet(lesson_name)
            #  写表头
            header_list = ['章节', '题目', '参考答案', '选项']
            # 写入表数据
            for pos, header in enumerate(header_list):
                worksheet.write(0, pos, label=header)
        # 写入表数据
        worksheet.write(count, 0, data_split_list[1])
        worksheet.write(count, 1, data_split_list[2])
        if data_split_list[3] == '0':
            worksheet.write(count, 2, "正确")
        elif data_split_list[3] == '1':
            worksheet.write(count, 2, "错误")
        else:
            worksheet.write(count, 2, data_split_list[3].replace("<br />", "\n"))
            if len(data_split_list) > 4:
                worksheet.write(count, 3, data_split_list[4][:-1].replace("$", "\n"))
        count += 1
        sum_count += 1
    workbook.save("章节练习题库_{}.xls".format(int(time.time())))
    print("共有练习题: {}".format(sum_count))


if __name__ == '__main__':
    to_xls()
