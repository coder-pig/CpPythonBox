# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : adb_util.py
   Author   : CoderPig
   date     : 2022-09-26 11:01 
   Desc     : 
-------------------------------------------------
"""
import os
import re
import subprocess
import time
from enum import Enum
from lxml import etree
from util.logger_util import default_logger
from util.os_util import is_win, is_mac

connect_device_pattern = re.compile("\n(.*?)\tdevice", re.S)  # 匹配设备的正则
pkg_act_pattern = re.compile(".* (.*?)/(.*?) ", re.S)  # 获取包名和Activity名的正则
chinese_pattern = re.compile("[\u4e00-\u9fa5]", re.S)  # 筛选中文的正则
size_pattern = re.compile(r"(\d+)x(\d+)", re.S)  # 获取屏幕尺寸的正则
bounds_pattern = re.compile(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]")  # 匹配控件区域的正则
t = time.time()
logger = default_logger()


class KeyEvent(Enum):
    """
    按键事件的枚举
    """
    HOME = 3
    BACK = 4
    POWER = 26
    DELETE = 67
    MENU = 82
    SCREEN_ON = 224
    SCREEN_OFF = 223
    SWITCH_APP = 187


def start_cmd(cmd):
    """
    执行命令
    :param cmd: 命令字符串
    :return: 执行后的输出结果列表
    """
    logger.info(cmd)
    proc = subprocess.Popen(cmd, shell=is_mac(), stdout=subprocess.PIPE)
    output_content = ""
    for result in proc.stdout.readlines():
        output_content += result.decode("utf-8")
    return output_content


def init():
    """
    连接设备，无设备连接会抛出异常
    :return:
    """
    output = start_cmd("adb devices")
    device_result = connect_device_pattern.search(output)
    if device_result:
        logger.info("当前连接设备：%s" % device_result.group(1))
    else:
        raise DeviceNotConnectException


def start_app(package_name):
    """
    启动APP
    :param package_name: 应用包名
    :return: 执行结果字符串
    """
    return start_cmd('adb shell monkey -p %s -c android.intent.category.LAUNCHER 1' % package_name)


def kill_app(package_name):
    """
    杀掉APP
    :param package_name: 应用包名
    :return:
    """
    return start_cmd('adb shell am force-stop %s' % package_name)


def current_pkg_activity():
    """
    获取当前页面的包名和Activity类名
    :return:
    """
    result = start_cmd('adb shell dumpsys activity top | grep ACTIVITY')
    # logger.info(result)
    if result is not None and len(result) > 0:
        match_result = re.search(pkg_act_pattern, result)
        if match_result:
            return match_result.group(1), match_result.group(2)
    return None


def key_event(event):
    """
    模拟按键
    :param event: 按键类型
    :return:
    """
    return start_cmd('adb shell input keyevent %d' % event.value)


def input_text(text):
    """
    当焦点处于某文本框时，模拟输入文本
    :param text: 输入文本内容
    :return:
    """
    match_result = re.findall(chinese_pattern, text)
    # 判断是否包含中文
    if len(match_result) > 0:
        return start_cmd('adb shell am broadcast -a ADB_INPUT_TEXT --es msg %s' % text)
    # 不包含中文调用原命令
    return start_cmd('adb shell input text %s' % text)


def swipe(start_x, start_y, end_x, end_y, duration=500):
    """
    滑动，从起始坐标点滑动到终点坐标
    :param start_x: 起始坐标点x坐标
    :param start_y: 起始坐标点y坐标
    :param end_x: 终点坐标点x坐标
    :param end_y: 终点坐标点y坐标
    :param duration: 滑动持续时间
    :return:
    """
    return start_cmd('adb shell input swipe %d %d %d %d %d' % (start_x, start_y, end_x, end_y, duration))


def click_xy(*args):
    """
    点击坐标点
    :param x: x坐标
    :param y: y坐标
    :return:
    """
    if len(args) == 1:
        return start_cmd('adb shell input tap %d %d' % (args[0][0], args[0][1]))
    elif len(args) == 2:
        return start_cmd('adb shell input tap %d %d' % (args[0], args[1]))


def long_click_xy(x, y, duration):
    """
    长按坐标点 (滑动模拟实现，当两坐标点差值足够小，Android系统就会认为我们进行了长按某个按钮的操作)
    :param x: x坐标
    :param y: y坐标
    :param duration: 长按时长，单位毫秒
    :return:
    """
    return start_cmd('adb shell input swipe %d %d %d %d %d' % (x, y, x + 1, y + 1, duration))


def click_area(*args):
    """
    传入左上右下坐标点，默认点击中间区域
    :param left: 左侧坐标
    :param top: 顶部坐标
    :param right: 右侧坐标
    :param bottom: 底部坐标
    :return:
    """
    if len(args) == 1:
        click_xy(int((args[0][0] + args[0][2]) / 2), int((args[0][1] + args[0][3]) / 2))
    elif len(args) == 4:
        click_xy(int((args[0] + args[2]) / 2), int((args[1] + args[3]) / 2))


def long_click_area(left, top, right, bottom, duration):
    """
    长按某个区域，默认点击中间区域
    :param left: 左侧坐标
    :param top: 顶部坐标
    :param right: 右侧坐标
    :param bottom: 底部坐标
    :param duration: 长按时长，单位毫秒
    :return:
    """
    x = int((left + right) / 2)
    y = int((top + bottom) / 2)
    return start_cmd('adb shell input swipe %d %d %d %d %d' % (x, y, x + 1, y + 1, duration))


def screenshot(save_dir=None):
    """
    获取手机截图，先截图后拉取(一步达成的方法好像有权限问题)
    :return: 截图文件的完整路径
    """
    sc_name = "%d.png" % (int(round(t * 1000)))
    start_cmd('adb shell screencap /sdcard/%s' % sc_name)
    sc_path = os.path.join(os.getcwd() if save_dir is None else save_dir, sc_name)
    start_cmd('adb pull /sdcard/%s %s' % (sc_name, sc_path))
    return sc_path


def screen_size():
    """
    获取屏幕分辨率
    :return: 屏幕的宽和高
    """
    size_result = re.search(size_pattern, start_cmd('adb shell wm size'))
    if size_result:
        return size_result.group(1), size_result.group(2)


def sleep(second):
    """
    进程休眠多少秒，支持小数，比如0.1就是100毫秒
    :param second: 休眠时长，单位秒
    :return:
    """
    time.sleep(second)


def current_ui_xml(save_dir=None):
    """
    获取当前页面的布局xml
    :param save_dir: 文件保存根目录
    :return: 布局xml文件的本地路径
    """
    ui_xml_name = "ui_%d.xml" % (int(round(time.time() * 1000)))
    start_cmd('adb shell /system/bin/uiautomator dump --compressed  /sdcard/%s' % ui_xml_name)
    ui_xml_path = os.path.join(os.getcwd() if save_dir is None else save_dir, ui_xml_name)
    start_cmd('adb pull /sdcard/%s %s' % (ui_xml_name, ui_xml_path))
    return ui_xml_path


class Node:
    """
    XML节点类
    """

    def __init__(self, index=None, text=None, resource_id=None, class_name=None, package=None, content_desc=None,
                 clickable=None,
                 bounds=None):
        self.index = index
        self.text = text
        self.resource_id = resource_id
        self.class_name = class_name
        self.package = package
        self.content_desc = content_desc
        self.bounds = bounds
        self.clickable = clickable
        self.nodes = []

    def add_node(self, node):
        self.nodes.append(node)

    def find_node_by_resource_id(self, resource_id):
        """
        根据resource_id查找node列表
        :param resource_id: 资源id字符串
        :return: 结点列表
        """
        if self.resource_id == resource_id:
            return self
        if len(self.nodes) > 0:
            for node in self.nodes:
                result = node.find_node_by_resource_id(resource_id)
                if result:
                    return result

    def find_nodes_by_resource_id(self, resource_id):
        """
        根据resource_id查找node
        :param resource_id: 资源id字符串
        :return: 结点
        """
        node_list = []
        if self.resource_id == resource_id:
            node_list.append(self)
        if len(self.nodes) > 0:
            for node in self.nodes:
                result = node.find_nodes_by_resource_id(resource_id)
                if result:
                    node_list += result
        return node_list


def analysis_ui_xml(xml_path):
    """
    解析ui.xml文件
    :param xml_path: xml文件路径
    :return: 节点实例
    """
    root = etree.parse(xml_path, parser=etree.XMLParser(encoding="utf-8"))
    root_node_element = root.xpath('/hierarchy/node')[0]  # 定位到根node节点
    node = analysis_element(root_node_element)
    # print_node(node)  # 打印看看效果
    return node


def analysis_element(element):
    """
    递归分析结点(转换为node对象)
    :param element:
    :return:
    """
    if element is not None and element.tag == "node":
        # 解析当前节点
        bounds_result = re.search(bounds_pattern, element.attrib['bounds'])
        node = Node(
            int(element.attrib['index']),
            element.attrib['text'],
            element.attrib['resource-id'],
            element.attrib['class'],
            element.attrib['package'],
            element.attrib['content-desc'],
            element.attrib['clickable'],
            (int(bounds_result[1]), int(bounds_result[2]), int(bounds_result[3]), int(bounds_result[4]))
        )
        # 解析子节点，递归调用
        child_node_elements = element.xpath('node')
        if len(child_node_elements) > 0:
            for child_node_element in child_node_elements:
                node_result = analysis_element(child_node_element)
                if node_result:
                    node.nodes.append(node_result)
        return node


def print_node(node, space_count=0):
    """
    递归打印结点信息
    :param node: 当前节点
    :param space_count: 前面的空格数，区分不同层级用
    :return:
    """
    widget_info = "%d - %s - %s - %s - %s - %s - %s -%s" % (
        node.index, node.text, node.resource_id, node.class_name, node.package, node.content_desc, node.clickable,
        node.bounds)
    logger.info(" " * (2 * space_count) + widget_info)
    for child_node in node.nodes:
        print_node(child_node, space_count + 1)


class DeviceNotConnectException(Exception):
    def __str__(self):
        logger.info("设备连接失败")


if __name__ == '__main__':
    # init()
    logger.info(current_pkg_activity())
