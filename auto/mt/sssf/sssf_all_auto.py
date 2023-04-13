# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : sssf_all_auto.py
   Author   : CoderPig
   date     : 2023-03-13 9:24
   Desc     : 谁是首富日常任务全自动脚本
-------------------------------------------------
"""
from util.adb_util import restart_app, sleep, click_xy, click_area, input_text, screenshot, swipe, long_click_xy
from util.file_util import get_temp_save_root_path, is_dir_existed
from util.logger_util import default_logger
from util.ocr_util import picture_local_ocr, picture_local_ocr_filter
import re

app_package_name = "com.sankuai.meituan"
logger = default_logger()
temp_dir = get_temp_save_root_path()


def start_game():
    """
    打开游戏
    """
    restart_app(app_package_name)
    sleep(0.3)
    click_area((211, 109, 579, 151))  # 点击搜索栏
    sleep(0.3)
    click_area((211, 109, 579, 151))  # 点击获取焦点
    input_text("谁是首富")
    click_area(928, 94, 1008, 94)  # 点击搜索
    sleep(10)  # 等待游戏加载完成
    # click_xy(932, 351)  # 关闭游戏公告
    # sleep(0.3)
    click_xy(548 , 1779)  # 点击开始游戏
    sleep(20)  # 等待游戏加载完成
    confirm_bound = picture_local_ocr_filter(screenshot(temp_dir), "确定")  # 点击确定
    if confirm_bound:
        click_area(confirm_bound[1])
    else:
        logger.info("未检测到确定按钮")
    sleep(1)
    logger.info("游戏正常打开...")


def vip_award():
    """
    领取vip奖励相关
    :return:
    """
    # 领取身份奖励
    click_xy(64, 147)  # 点击头像
    click_xy(508, 1171)  # 点击身份奖励
    click_xy(516, 1419)  # 点击领取奖励
    click_xy(336, 1547)  # 点击空白区域
    click_xy(1004, 571)  # 点击x
    click_xy(1032, 611)  # 点击x
    logger.info("身份奖励已领取...")
    # 领取游戏会员
    click_xy(60, 323)  # 点击游戏会员
    click_xy(832, 1095)  # 领取月度会员
    click_xy(336, 1547)  # 点击空白区域
    click_xy(224, 1723)  # 领取终身会员
    click_xy(336, 1547)  # 点击空白区域
    click_xy(1032, 251)  # 点击x
    logger.info("游戏会员奖励已领取...")
    # 签到与邮箱
    click_xy(24, 803)  # 点击展开按钮
    click_xy(56, 831)  # 点击签到
    sleep(1)
    receive_bound = picture_local_ocr_filter(screenshot(temp_dir), "领取")  # 点击领取
    if receive_bound:
        click_area(receive_bound[1])
    sleep(1)
    click_xy(135, 1943)  # 点击空白区域
    click_xy(1040, 235)  # 点击x
    logger.info("每日签到已完成...")
    click_xy(24, 803)  # 点击展开按钮
    click_xy(72, 975)  # 点击邮件
    click_xy(736, 1567)  # 点击一键领取
    click_xy(736, 1567)  # 点击一键领取
    click_xy(135, 1943)  # 点击空白区域
    sleep(1)
    logger.info("邮件奖品已领取...")


def assistant_daily_tasks():
    """
    助理日常
    :return:
    """
    # click_xy(64, 2023)
    # # 环球打卡
    # click_xy(708, 695)
    # click_xy(540, 1875)  # 点击打卡
    # sleep(2)
    # click_xy(540, 1875)  # 点击打卡
    # click_xy(932, 1951)  # 点击赠送出行卡
    # click_xy(924, 971)
    # click_xy(924, 1167)
    # click_xy(924, 1527)
    # click_xy(960, 435)
    # click_xy(1020, 147)  # 点击x
    # logger.info("环球打卡任务已完成...")
    # # 助理
    # click_xy(536, 1119)  # 点击助理
    # click_xy(716, 1951)  # 勾选一键团建
    # click_xy(800, 1843)  # 点击一键团建
    # click_xy(336, 1547)  # 点击空白区域
    # click_xy(88, 1863)  # 点击返回
    # logger.info("助理任务已完成...")
    # # 实习生
    # click_xy(660, 1327)  # 点击实习生
    # for i in range(10):
    #     click_xy(260, 1887)  # 摆摊10次
    #     click_xy(56, 1903)  # 点击空白区域
    #
    # for i in range(3):
    #     click_xy(1000, 1327)  # 电话协助
    #     sleep(2)
    # click_xy(953, 363)  # 点击x
    click_xy(668, 2015)  # 点击实习
    click_xy(80, 1231)  # 点击留学派遣
    click_xy(532, 495)  # 点击美食之都
    click_xy(800, 1811)  # 点击双人留学
    click_xy(424, 1651)  # 选中第二个留学生
    click_xy(80, 1231)  # 点击留学派遣
    click_xy(532, 495)  # 点击美食之都
    click_xy(800, 1811)  # 点击双人留学
    click_xy(660, 1667)  # 选中第三个留学生
    click_xy(80, 1231)  # 点击留学派遣
    click_xy(532, 495)  # 点击美食之都
    click_xy(800, 1811)  # 点击双人留学
    click_xy(100, 1679)  # 点击返回
    click_xy(540, 2018)  # 点击地图
    sleep(0.5)
    logger.info("留学生任务已完成...")


def finance_daily_tasks():
    """
    金融日常任务
    :return:
    """
    # 街区经营
    # click_xy(872, 2041)  # 点击金融
    # sleep(0.8)
    # click_xy(596, 819)  # 点击街区经营
    # for i in range(1, 20):
    #     click_xy(548, 1751)  # 点击一键巡视
    #     click_xy(336, 1547)  # 点击空白区域
    #     click_xy(68, 399)  # 点击事件
    #     click_xy(752, 1623)  # 点击投资
    #     click_xy(336, 1547)  # 点击空白区域
    #     click_xy(960, 351)  # 点击x
    # click_xy(336, 1547)  # 点击空白区域
    # logger.info("街区经营任务已完成...")

    # 排位战
    click_xy(872, 2041)  # 点击金融
    sleep(0.8)
    click_xy(532, 1307)  # 点击商界排位战
    for i in range(0, 30):
        logger.info("执行第【{}\\{}】次对决".format(i + 1, 30))
        click_xy(552, 1359)  # 点击开始
        click_xy(536, 1839)  # 点击开始
        click_xy(916, 1771)  # 点击跳过
        click_xy(336, 1547)  # 点击空白区域
        click_xy(336, 1547)  # 点击空白区域
        sleep(0.2)
    logger.info("商界排位战任务已完成...")
    click_xy(140, 1007)  # 点击每日挑战可领取
    for i in range(10):
        click_xy(868, 675)  # 点击领取
        click_xy(336, 1547)  # 点击空白区域
    click_xy(948, 423)
    logger.info("商界排位战奖励已领取...")

    # 名车博览会
    click_xy(872, 2041)  # 点击金融
    sleep(0.8)
    click_xy(564, 1711)  # 点击名车博览会
    swipe(500, 1500, 500, 500, 200)
    sleep(3)
    swipe(500, 1500, 500, 1200)
    sleep(1)
    target_list = []
    ocr_result_dict = picture_local_ocr(screenshot(temp_dir))
    if ocr_result_dict:
        for orc_key in ocr_result_dict.keys():
            if "当前收益" in orc_key:
                target_list.append(int((ocr_result_dict[orc_key][1] + ocr_result_dict[orc_key][3]) / 2))
    click_point_x = 776
    click_point_y = target_list[len(target_list) - 1] - 130
    click_xy(click_point_x, click_point_y)  # 找到停车位然后双击
    click_xy(click_point_x, click_point_y)
    click_xy(876, 483)  # 点击派遣
    sleep(1)
    click_xy(336, 1547)  # 点击空白区域
    logger.info("名车博览会任务已完成...")

    # 商战段位
    click_xy(716, 2047)  # 点击科技
    click_xy(872, 2041)  # 点击金融
    sleep(1.5)
    swipe(100, 1500, 100, 1300)
    commercial_war_bound = picture_local_ocr_filter(screenshot(temp_dir), "可重置次数")
    if commercial_war_bound:
        click_area(commercial_war_bound[1])
    click_xy(328, 1775)
    click_xy(684, 1235)
    click_xy(741, 1787)
    sleep(2)
    click_xy(569, 1555)
    logger.info("商战段位任务已完成...")

    # 游园会
    click_xy(716, 2047)  # 点击科技
    click_xy(872, 2041)  # 点击金融
    sleep(1.5)
    swipe(100, 1500, 100, 1000)
    sleep(1)
    garden_bound = picture_local_ocr_filter(screenshot(temp_dir), "园")
    if garden_bound:
        click_area(garden_bound[1])
    click_xy(336, 1547)  # 点击空白区域
    click_xy(512, 1823)  # 点击逛展
    sleep(0.8)
    click_xy(540, 1127)  # 选中摊位
    click_xy(820, 1195)  # 点击加号
    click_xy(820, 1195)  # 点击加号
    click_xy(556, 1355)  # 点击购买
    click_xy(88, 1811)  # 点击返回
    logger.info("游园会任务已完成...")

    # 商业风云
    click_xy(716, 2047)  # 点击科技
    click_xy(872, 2041)  # 点击金融
    sleep(1.5)
    swipe(100, 1500, 100, 1000)
    sleep(1)
    commercial_war_bound = picture_local_ocr_filter(screenshot(temp_dir), "云")
    if commercial_war_bound:
        click_area(commercial_war_bound[1])
        sleep(1)
    click_xy(349, 1487)  # 选中榕城
    click_xy(792, 1831)  # 点击极速探索
    click_xy(876, 1215)  # 点击最大
    click_xy(528, 1423)  # 点击使用
    click_xy(336, 1547)  # 点击空白区域
    click_xy(336, 1547)  # 点击空白区域
    click_xy(940, 407)  # 点击空白区域
    logger.info("商业风云任务已完成...")

    # 环球鉴宝
    click_xy(716, 2047)  # 点击科技
    click_xy(872, 2041)  # 点击金融
    sleep(1.5)
    swipe(100, 1500, 100, 1000)
    sleep(1.5)
    swipe(100, 1800, 100, 1000)
    sleep(1)
    treasure_bound = picture_local_ocr_filter(screenshot(temp_dir), "宝")
    if treasure_bound:
        click_area(treasure_bound[1])
        sleep(1)
    for i in range(3):
        click_xy(232, 219)
        click_xy(984, 531)
        click_xy(336, 1547)  # 点击空白区域
    logger.info("环球鉴宝任务已完成...")

    # 全球贸易
    click_xy(716, 2047)  # 点击科技
    click_xy(872, 2041)  # 点击金融
    sleep(1.5)
    swipe(100, 1500, 100, 1000)
    sleep(1.5)
    swipe(100, 1800, 100, 1000)
    sleep(1)
    business_bound = picture_local_ocr_filter(screenshot(temp_dir), "易")
    if business_bound:
        click_area(business_bound[1])
        sleep(1)
    attack_count_pattern = re.compile(r'.*?: (\d+)', re.S)  # 获得剩余次数的正则
    while True:
        attack_ocr_result = picture_local_ocr_filter(screenshot(temp_dir), "剩余次数")
        if attack_ocr_result:
            attack_match_result = attack_count_pattern.search(attack_ocr_result[0])
            if attack_match_result is not None and int(attack_match_result.group(1)) > 0:
                click_xy(852, 239)  # 刷新订单
                click_xy(356, 803)  # 选中第一个
                click_xy(724, 1571)  # 点击挑战
                click_xy(920, 1767)  # 点击跳过
                click_xy(336, 1547)  # 点击空白区域
                click_xy(256, 1243)  # 选中第二个
                click_xy(724, 1571)  # 点击挑战
                click_xy(920, 1767)  # 点击跳过
                click_xy(336, 1547)  # 点击空白区域
                click_xy(708, 1383)  # 选中第三个
                click_xy(724, 1571)  # 点击挑战
                click_xy(920, 1767)  # 点击跳过
                click_xy(336, 1547)  # 点击空白区域
                click_xy(816, 939)  # 选中第四个
                click_xy(724, 1571)  # 点击挑战
                click_xy(920, 1767)  # 点击跳过
                click_xy(336, 1547)  # 点击空白区域
                click_xy(524, 1843)  # 点击合成
                click_xy(336, 1547)  # 点击空白区域
            else:
                break
        else:
            break
    logger.info("全球贸易任务已完成...")

    # 萌宠收容
    # click_xy(716, 2047)  # 点击科技
    # click_xy(872, 2041)  # 点击金融
    # sleep(1.5)
    # swipe(100, 1800, 100, 1000)
    # sleep(1.5)
    # swipe(100, 1800, 100, 1000)
    # sleep(1.5)
    # click_xy(536, 1371)
    # for i in range(10):
    #     click_xy(580, 1859)
    #     click_xy(884, 1603)  # 点击跳过
    #     click_xy(336, 1547)  # 点击空白区域
    # logger.info("萌宠收容任务已完成...")

    # 航空联盟
    click_xy(716, 2047)  # 点击科技
    click_xy(872, 2041)  # 点击金融
    sleep(1.5)
    swipe(100, 1800, 100, 1000)
    sleep(1.5)
    swipe(100, 1800, 100, 1000)
    sleep(1.5)
    click_xy(548, 1747)
    click_xy(832, 267)
    click_xy(980, 243)
    click_xy(336, 1547)  # 点击空白区域
    for i in range(3):
        click_xy(476, 587)
        click_xy(336, 1547)  # 点击空白区域
    sleep(0.8)
    click_xy(88, 1831)  # 点击返回
    click_xy(540, 2018)  # 点击地图
    sleep(1)
    logger.info("航空联盟任务已完成...")


def ranking_list_tasks():
    """
    排行榜点赞
    :return:
    """
    click_xy(988, 371)
    # 本服
    sleep(1)
    click_xy(1012, 1127)  # 实力榜点赞
    click_xy(144, 831)  # 切换能力榜
    click_xy(1012, 1127)  # 能力榜点赞
    click_xy(144, 923)  # 商战日榜
    click_xy(968, 2031)
    click_xy(144, 1025)  # 商战七日榜
    click_xy(968, 2031)
    click_xy(144, 1123)  # 地图榜
    click_xy(968, 2031)
    click_xy(144, 1211)  # 段位榜
    click_xy(968, 2031)
    # 跨服
    click_xy(144, 1399)  # 实力榜
    sleep(0.5)
    click_xy(1008, 1600)
    click_xy(144, 1495)  # 能力榜
    sleep(0.5)
    click_xy(1000, 1600)
    click_xy(144, 1595)  # 商会榜
    sleep(0.5)
    click_xy(968, 2031)
    click_xy(144, 1695)  # 地图榜
    sleep(0.5)
    click_xy(968, 2031)
    click_xy(144, 1791)  # 人气榜
    sleep(0.5)
    click_xy(968, 2031)
    click_xy(144, 1891)  # 舒适榜
    sleep(0.5)
    click_xy(968, 2031)
    sleep(0.8)
    click_xy(88, 1831)  # 点击返回
    logger.info("排行榜点赞任务已完成...")


def garden_tasks():
    """
    家园任务
    :return:
    """
    click_xy(72, 1607)
    sleep(0.3)
    # 花园
    click_xy(592, 1439)  # 点击花园
    click_xy(856, 2000)  # 点击收获
    click_xy(152, 1331)  # 点击第一个好友
    click_xy(856, 2000)  # 点击收获
    click_xy(336, 1547)  # 点击空白区域
    click_xy(152, 1435)  # 点击第二个好友
    click_xy(856, 2000)  # 点击收获
    click_xy(336, 1547)  # 点击空白区域
    click_xy(152, 1519)  # 点击第三个好友
    click_xy(856, 2000)  # 点击收获
    click_xy(336, 1547)  # 点击空白区域
    click_xy(96, 2003)  # 点击我的家园
    click_xy(96, 2003)  # 点击一键种植
    click_xy(992, 247)  # 点击花园商店
    click_xy(980, 2039)  # 点击快速购买
    click_xy(940, 2000)  # 点击确定
    click_xy(88, 1863)  # 点击返回
    logger.info("花园日常任务已完成...")
    # 茶园
    click_xy(712, 1119)  # 点击花园
    click_xy(856, 2000)  # 点击收获
    click_xy(152, 1331)  # 点击第一个好友
    click_xy(856, 2000)  # 点击收获
    click_xy(336, 1547)  # 点击空白区域
    click_xy(152, 1435)  # 点击第二个好友
    click_xy(856, 2000)  # 点击收获
    click_xy(336, 1547)  # 点击空白区域
    click_xy(152, 1519)  # 点击第三个好友
    click_xy(856, 2000)  # 点击收获
    click_xy(336, 1547)  # 点击空白区域
    click_xy(96, 2003)  # 点击我的家园
    click_xy(96, 2003)  # 点击一键种植
    click_xy(992, 247)  # 点击茶园商店
    click_xy(980, 2039)  # 点击快速购买
    click_xy(940, 2000)  # 点击确定
    click_xy(72, 1939)  # 点击返回
    click_xy(92, 1827)  # 点击返回
    logger.info("茶园日常任务已完成...")
    # 庭院
    click_xy(740, 791)  # 点击庭院
    sleep(0.8)
    click_xy(1012, 403)  # 点击庭院2层
    click_xy(116, 1827)  # 点击娱乐室
    click_xy(788, 1739)  # 点击一键领取
    click_xy(549, 1719)  # 点击确定
    click_xy(321, 1719)  # 点击一键上阵
    click_xy(957, 327)  # 点击x
    click_xy(85, 1167)  # 点击返回
    logger.info("庭院日常任务已完成...")
    # 舞会
    click_xy(24, 559)  # 点击舞厅
    click_xy(300, 707)  # 点击+号
    sleep(0.8)
    click_xy(592, 303)  # 选中1个助理
    click_xy(592, 599)  # 选中2个助理
    click_xy(592, 935)  # 选中3个助理
    click_xy(592, 1203)  # 选中4个助理
    click_xy(592, 1535)  # 选中5个助理
    click_xy(892, 1991)  # 点击参加舞会
    click_xy(84, 1667)  # 点击返回
    logger.info("舞会日常任务已完成...")
    # 宠物乐园
    click_xy(116, 715)  # 点击宠物乐园
    sleep(0.5)
    click_xy(840, 279)  # 点击宠物记录
    sleep(0.8)
    click_xy(532, 1667)  # 点击一键领取
    click_xy(948, 300)  # 点击x
    click_xy(428, 2023)  # 点击升级
    click_xy(1000, 455)  # 选中装备
    click_xy(868, 535)  # 点击升级
    click_xy(545, 1419)  # 点击升级
    click_xy(948, 723)  # 点击x
    click_xy(956, 300)  # 点击x
    for i in range(18):
        click_xy(160, 1623)
        for j in range(5):
            click_xy(136, 1079)  # 点击抚摸
        swipe(1016, 1619, 900, 1631, 1000)
        sleep(0.5)
    click_xy(476, 1631)
    for j in range(5):
        click_xy(136, 1079)  # 点击抚摸
    click_xy(768, 1631)
    for j in range(5):
        click_xy(136, 1079)  # 点击抚摸
    click_xy(1028, 1631)
    for j in range(5):
        click_xy(136, 1079)  # 点击抚摸
    click_xy(856, 2023)  # 点击扭蛋
    click_xy(788, 1471)  # 点击抓取
    click_xy(76, 1687)  # 点击返回
    click_xy(336, 1547)  # 点击空白区域
    click_xy(80, 1831)  # 点击返回回到主页面
    logger.info("宠物乐园日常任务已完成...")


def island_tasks():
    """
    岛屿任务
    :return:
    """
    click_xy(216, 1611)
    sleep(1)
    click_xy(148, 483)  # 点击藏宝图
    click_xy(336, 1547)  # 点击空白区域
    click_xy(984, 663)  # 点击海岛
    click_xy(560, 723)  # 选中海岛
    click_xy(764, 1700)  # 点击观光
    click_xy(336, 1547)  # 点击空白区域
    click_xy(948, 343)  # 点击x
    click_xy(96, 1891)  # 点击返回
    for i in range(10):
        click_xy(968, 487)  # 点击钓鱼
        click_xy(528, 1700)  # 点击抛竿
        sleep(5)
        long_click_xy(528, 1700, 3000)
        sleep(1)
        click_xy(764, 1591)  # 点击入护
    click_xy(80, 1819)  # 点击返回
    click_xy(80, 1819)  # 点击返回
    logger.info("海岛日常任务已完成...")


def all_diary_task():
    """
    执行所有日常任务的Task
    :return:
    """
    # start_game()
    # vip_award()
    # finance_daily_tasks()
    # ranking_list_tasks()
    assistant_daily_tasks()
    garden_tasks()
    island_tasks()


if __name__ == '__main__':
    is_dir_existed(temp_dir, is_recreate=True)
    all_diary_task()
