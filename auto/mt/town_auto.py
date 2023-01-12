# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : town_auto.py
   Author   : CoderPig
   date     : 2022-12-23 14:12 
   Desc     : 美团-美团小镇自动做任务
-------------------------------------------------
"""
from util.adb_util import *
from util.file_util import *
from util.logger_util import default_logger
from util.ocr_util import picture_local_ocr

logger = default_logger()
mt_pkg_name = "com.sankuai.meituan"
temp_dir = get_temp_save_root_path()


# 浏览10s
def browser_10s():
    sleep(11)
    key_event(KeyCode.BACK)
    sleep(1)
    click_area(470, 1324, 611, 1403)


# 拜访好友
def visit_friend():
    sleep(3)
    while True:
        click_area(478, 1696, 602, 1743)  # 点击骰子
        ocr_dict = picture_local_ocr(screenshot(temp_dir))
        for ocr in ocr_dict.keys():
            if "确定" in ocr:
                click_area(*ocr_dict[ocr])
                sleep(3)
                return
        sleep(3)


# 猜个杯
def guess_cup():
    sleep(8)
    click_xy(546, 1300)
    sleep(4)
    ocr_dict = picture_local_ocr(screenshot(temp_dir))
    for ocr in ocr_dict.keys():
        if "确定" in ocr:
            click_area(*ocr_dict[ocr])
            sleep(3)


# 盲盒抽奖
def blind_box(box_list):
    for box in box_list[:2]:
        click_area(*box)
        sleep(4)
        click_area(453, 1459, 628, 1555)
    sleep(2)
    click_xy(927, 451)
    sleep(3)


# 金库
def treasury():
    click_xy(769, 1529)
    sleep(2)
    click_xy(737, 1097)
    sleep(2)
    click_xy(293, 1497)
    sleep(4)
    click_area(451, 1458, 629, 1555)
    sleep(3)


# 投骰子
def roll():
    logger.info("投骰子~")
    while True:
        click_area(478, 1696, 602, 1743)  # 点击骰子
        sleep(8)
        ocr_result_dict = picture_local_ocr(screenshot(temp_dir))
        print(ocr_result_dict)
        # 判断任务类型
        is_browser_10s_area = None
        is_visit_friend_area = None
        is_visit_friend_click_area = None
        is_guess_cup = None
        is_blind_box = None
        is_blind_box_list = []
        is_treasury = None
        is_not_roll_area = None
        continue_game = None
        confirm = None
        receive = None
        for result in ocr_result_dict.keys():
            if "解锁" in result:
                is_browser_10s_area = ocr_result_dict[result]
            elif "拜访好友" in result:
                is_visit_friend_area = ocr_result_dict[result]
            elif "获得" in result:
                if is_visit_friend_click_area is None:
                    is_visit_friend_click_area = ocr_result_dict[result]
            elif "猜个杯子" in result:
                is_guess_cup = ocr_result_dict[result]
            elif "盲盒抽奖" in result:
                is_blind_box = ocr_result_dict[result]
            elif "试试手气" in result:
                is_blind_box_list.append(ocr_result_dict[result])
            elif "的金库" in result:
                is_treasury = ocr_result_dict[result]
            elif "不足" in result:
                is_not_roll_area = ocr_result_dict[result]
            elif "继续游戏" in result:
                continue_game = ocr_result_dict[result]
            elif "确定" in result:
                confirm = ocr_result_dict[result]
            elif "领取" in result:
                receive = ocr_result_dict[result]
        if is_browser_10s_area:
            logger.info("执行浏览10s任务")
            click_area(*is_browser_10s_area)
            browser_10s()
            continue
        if is_visit_friend_area:
            logger.info("执行拜访好友任务")
            click_area(*is_visit_friend_click_area)
            visit_friend()
            continue
        if is_guess_cup:
            logger.info("执行猜个杯子任务")
            guess_cup()
            continue
        if is_blind_box:
            logger.info("执行盲盒抽奖任务")
            blind_box(is_blind_box_list)
            continue
        if is_treasury:
            logger.info("执行金库任务")
            treasury()
            continue
        if is_not_roll_area:
            logger.info("没骰子了，续一下")
            click_area(520, 1194, 645, 1264)
            browser_10s()
            sleep(1)
            click_area(451, 1458, 630, 1555)
            sleep(2)
            continue
        if continue_game:
            logger.info("被暴击狗盯上了，继续游戏")
            click_area(*continue_game)
            sleep(11)
            key_event(KeyCode.BACK)
            sleep(1)
            continue
        if confirm:
            logger.info("发现确定按钮，点击")
            click_area(*confirm)
            continue
        if receive:
            logger.info("发现领取按钮，点击")
            click_area(*receive)
            continue
        logger.info("匹配不到任务类型")


# 领奖励
def receive_rewards():
    logger.info("执行领取奖励任务")
    is_list_expand = False
    ocr_result_dict = picture_local_ocr(screenshot(temp_dir))
    for ocr in ocr_result_dict.keys():
        if "每日任务" in ocr:
            is_list_expand = True
    if not is_list_expand:
        click_xy(158, 1849)
    while True:
        count = 0
        if not receive_rewards_detail():
            swipe(589, 1267, 589, 1055)
            count += 1
        if count == 5:
            return
        sleep(2)


# 领取奖励的具体操作
def receive_rewards_detail():
    have_task_flag = False
    ocr_result_dict = picture_local_ocr(screenshot(temp_dir))
    print(ocr_result_dict)
    for ocr in ocr_result_dict.keys():
        if "可领取" in ocr:
            have_task_flag = True
            click_area(*ocr_result_dict[ocr])
            sleep(2)
            click_area(451, 1456, 629, 1553)
        elif "去浏览" in ocr:
            have_task_flag = True
            click_area(*ocr_result_dict[ocr])
            browser_10s()
    return have_task_flag


# 打开APP进入美团小镇
def to_mt_town():
    start_app(mt_pkg_name)
    sleep(2)
    click_area(856, 2030, 1068, 2160)  # 点击我的
    sleep(3)
    click_area(637, 1399, 835, 1558)  # 点击美团小镇
    sleep(3)


if __name__ == '__main__':
    is_dir_existed(temp_dir, is_recreate=True)
    init()
    # to_mt_town()
    # 一直投骰子
    roll()
    # 骰子都用完了，可以领取奖励，然后再roll
    # receive_rewards()
