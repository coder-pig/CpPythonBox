# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : boss_spider.py
   Author   : CoderPig
   date     : 2023-02-23 17:33 
   Desc     : boss直聘爬虫-使用浏览器模拟访问
-------------------------------------------------
"""
import asyncio
import os

import requests as r
from lxml import etree

from util.file_util import is_dir_existed, write_text_to_file, read_list_from_file, fetch_all_file_list
from util.logger_util import default_logger
from util.pyppeteer_utils import PyBrowser
import random

logger = default_logger()
output_dir = os.path.join(os.getcwd(), "output")
city_file = os.path.join(output_dir, "city.txt")
district_file_dir = os.path.join(output_dir, "district")
job_file_dir = os.path.join(output_dir, "job")
default_header = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/110.0.0.0 Safari/537.36 ',
}
base_url = "https://www.zhipin.com{}"
city_group_url = base_url.format("/wapi/zpCommon/data/cityGroup.json")
business_district_url = base_url.format("/wapi/zpgeek/businessDistrict.json?cityCode={}")
job_list_url = base_url.format("/wapi/zpgeek/search/joblist.json?scene=1&query=%{}&city={"
                               "}&experience=&degree=&industry=&scale=&stage=&position=&jobType=&salary"
                               "=&multiBusinessDistrict={"
                               "}&multiSubway=&page={}&pageSize=30")
job_list_page_url = base_url.format("/web/geek/job?query={}&city={}&areaBusiness={}:{}&page={}")
keyword = "Android"


def fetch_city():
    city_resp = r.get(city_group_url, headers=default_header)
    if city_resp:
        if city_resp.status_code == 200:
            content = ""
            for city in city_resp.json()['zpData']['hotCityList'][1:]:
                content += "{}|{}\n".format(city['name'], city['code'])
            write_text_to_file(content.rstrip(), city_file)


def fetch_district():
    city_list = read_list_from_file(city_file)
    for city in city_list:
        city, code = city.split("|")
        resp = r.get(business_district_url.format(code), headers=default_header)
        logger.info("爬取：{}".format(resp.url))
        if resp.status_code == 200:
            content = ""
            for level_model in resp.json()['zpData']['businessDistrict']['subLevelModelList']:
                content += "{}|{}|{}|{}\n".format(city, code, level_model['name'], level_model['code'])
            write_text_to_file(content.rstrip(), os.path.join(district_file_dir, "{}_{}.txt".format(city, code)))


def fetch_district_and_place():
    city_list = read_list_from_file(city_file)
    for city in city_list:
        city, code = city.split("|")
        resp = r.get(business_district_url.format(code), headers=default_header)
        logger.info("爬取：{}".format(resp.url))
        if resp.status_code == 200:
            content = ""
            for level_model in resp.json()['zpData']['businessDistrict']['subLevelModelList']:
                place_level = level_model['subLevelModelList']
                if place_level:
                    for place in level_model['subLevelModelList']:
                        content += "{}|{}|{}|{}|{}|{}\n".format(city, code, level_model['name'], level_model['code'],
                                                                place['name'], place['code'])
            write_text_to_file(content.rstrip(), os.path.join(district_file_dir, "{}_{}.txt".format(city, code)))


def fetch_job():
    district_file_list = fetch_all_file_list(district_file_dir)
    for district_file in district_file_list[:1]:
        for district_list in read_list_from_file(district_file)[:1]:
            city_name, city_code, district_name, district_code = district_list.split("|")
            page_count = request_job_url(city_name, city_code, district_name, district_code, 1)
            if page_count:
                for page in range(2, int(page_count)):
                    request_job_url(city_name, city_code, district_name, district_code, page)


def request_job_url(city_name, city_code, district_name, district_code, page):
    resp = r.get(job_list_url.format(keyword, city_code, district_code, page), headers=default_header)
    logger.info("爬取：{}".format(resp.url))
    logger.info(resp.text)
    if resp.status_code == 200:
        resp_json = resp.json()
        if resp_json['code'] == 0:
            zp_data = resp_json['zpData']
            save_file = os.path.join(job_file_dir, "{}_{}.txt".format(city_name, district_name))
            for job in zp_data['jobList']:
                write_text_to_file(analyze_job_list(job), save_file, "a+")
            if page == 1:
                total_count = zp_data['totalCount']
                page_count = int(int(total_count) / 30)
                return page_count
        else:
            request_job_url(city_name, city_code, district_name, district_code, page)


def analyze_job_list(job):
    return "{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}|{}".format(
        job['jobName'], job['salaryDesc'],
        job['jobExperience'], job['jobDegree'],
        job['brandName'], job['brandStageName'], job['brandIndustry'], job['brandScaleName'],
        ','.join(job['skills']), job['cityName'], job['areaDistrict'], job['businessDistrict'],
        ','.join(job['welfareList'])
    )


async def login():
    browser = PyBrowser()
    await browser.get_browser()
    await browser.open("https://www.zhipin.com/web/user/?ka=header-login")
    logger.info("等待扫码, 300s后自动关闭")
    await asyncio.sleep(300)


async def fetch_job():
    browser = PyBrowser()
    await browser.get_browser()
    # 读取区域列表
    district_file_list = fetch_all_file_list(district_file_dir)
    for district_file in district_file_list:
        # 过滤深圳地区数据
        if "深圳" in district_file:
            for district_list in read_list_from_file(district_file):
                city_name, city_code, district_name, district_code, place_name, place_code = district_list.split("|")
                for page in range(1, 11):
                    request_url = job_list_page_url.format(keyword, city_code, district_code, place_code, page)
                    await browser.page.goto(request_url)
                    logger.info("请求【{}-{}-{}】第{}页数据：{}".format(city_name, district_name, place_name, page, request_url))
                    sleep_time = random.randint(15, 20)
                    logger.info("休眠{}秒防封...".format(sleep_time))
                    await asyncio.sleep(sleep_time)
                    # 获取网页源码
                    page_source = await browser.page.content()
                    # 数据保存文件名
                    city_dir = os.path.join(job_file_dir, city_name)
                    is_dir_existed(city_dir)
                    data_file = os.path.join(city_dir, "{}_{}.txt".format(city_name, district_name))
                    # 提取所需元素
                    selector = etree.HTML(page_source)
                    try:
                        job_card_list = selector.xpath('//li[@class="job-card-wrapper"]')
                        if job_card_list is None or len(job_card_list) == 0:
                            logger.info("【{}-{}-{}】第{}页未检测到数据，直接跳过...".format(city_name, district_name, place_name, page))
                            break
                        else:
                            for job_card in job_card_list:
                                tag_node_list = job_card.xpath('.//div[@class="job-card-footer clearfix"][1]/ul/li')
                                tag_list = []
                                for tag_node in tag_node_list:
                                    tag_list.append(tag_node.text)
                                company_node_list = job_card.xpath('.//ul[@class="company-tag-list"]/li')
                                company_tag_list = []
                                for company_node in company_node_list:
                                    company_tag_list.append(company_node.text)
                                content = "{}|{}|{}|{}|{}|{}|{}|{}".format(
                                    job_card.xpath('.//span[@class="job-name"]')[0].text,
                                    job_card.xpath('.//span[@class="salary"]')[0].text,
                                    job_card.xpath('.//ul[@class="tag-list"]/li')[0].text,  # 工作年限
                                    job_card.xpath('.//ul[@class="tag-list"]/li')[1].text,  # 学历要求
                                    job_card.xpath('.//h3[@class="company-name"]/a')[0].text,  # 公司名称
                                    "，".join(company_tag_list),
                                    "，".join(tag_list),  # 公司标签
                                    job_card.xpath('.//div[@class="info-desc"]')[0].text,  # 公司备注信息
                                )
                                write_text_to_file(content, data_file, "a+")
                    except Exception as e:
                        logger.error(e)


if __name__ == '__main__':
    is_dir_existed(output_dir)
    is_dir_existed(district_file_dir)
    is_dir_existed(job_file_dir)
    # fetch_city()
    # fetch_district_and_place()
    # asyncio.get_event_loop().run_until_complete(login())
    asyncio.get_event_loop().run_until_complete(fetch_job())
