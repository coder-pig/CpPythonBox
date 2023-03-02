# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : data_wash.py
   Author   : CoderPig
   date     : 2023-02-24 12:47 
   Desc     : 爬取到的数据进行清洗
-------------------------------------------------
"""
import os
import xlwt
import time

from util.file_util import fetch_all_file_list, read_list_from_file, write_text_to_file

output_dir = os.path.join(os.getcwd(), "output")
job_data_dir = os.path.join(output_dir, "job")
dirty_data_file = os.path.join(output_dir, "dirty_data.txt")


def wash_write_excel():
    # 获得城市列表文件夹
    city_dir_list = fetch_all_file_list(job_data_dir)
    # 创建workbook并设置编码
    workbook = xlwt.Workbook(encoding='utf-8')
    # 总共有多少条记录
    sum_count = 0
    for city_folder in city_dir_list:
        # 根据文件夹获得城市名称
        city_name = os.path.basename(city_folder)
        worksheet = workbook.add_sheet(city_name)
        # 写入表头
        header_list = ['岗位名称', '薪资', '工作年限', '学历要求', '公司名', '产业类型', '融资情况', '人数规模', '标签', '公司福利']
        # 写入表数据
        for pos, header in enumerate(header_list):
            worksheet.write(0, pos, label=header)
        # 写入表数据
        file_list = fetch_all_file_list(city_folder)
        count = 1  # 行计数器
        for file in file_list:
            job_list = read_list_from_file(file)
            for job in job_list:
                job_split_list = job.split("|")
                if "产品" in job_split_list[0]:
                    if len(job_split_list) == 8:
                        worksheet.write(count, 0, job_split_list[0] if job_split_list[0] != "None" else "")  # 岗位名称
                        worksheet.write(count, 1, job_split_list[1] if job_split_list[1] != "None" else "")  # 薪资
                        worksheet.write(count, 2, job_split_list[2] if job_split_list[2] != "None" else "")  # 工作年限
                        worksheet.write(count, 3, job_split_list[3] if job_split_list[3] != "None" else "")  # 学历要求
                        worksheet.write(count, 4, job_split_list[4] if job_split_list[4] != "None" else "")  # 公司名称
                        # 产业类型、融资情况、人数规模
                        company_info_split_list = job_split_list[5].split('，')
                        for index, info in enumerate(company_info_split_list):
                            if index < 3:
                                worksheet.write(count, 5 + index, company_info_split_list[index])
                        worksheet.write(count, 8, job_split_list[6] if job_split_list[6] != "None" else "")  # 公司名称
                        worksheet.write(count, 9, job_split_list[7] if job_split_list[7] != "None" else "")  # 公司名称
                        count += 1
                        sum_count += 1
                    else:
                        write_text_to_file(job, dirty_data_file, "a+")
    workbook.save("BOSS直聘产品经理岗位数据_{}.xls".format(int(time.time())))
    print("总共采集到有效数据【{}】条".format(sum_count))


def count_record():
    sum_count = 0
    city_dir_list = fetch_all_file_list(job_data_dir)
    for city_folder in city_dir_list:
        file_list = fetch_all_file_list(city_folder)
        for file in file_list:
            sum_count += len(read_list_from_file(file))
    print("总共采集到数据【{}】条".format(sum_count))


if __name__ == '__main__':
    wash_write_excel()
