# CpPythonBox

自用练手py脚本合集

## auto（自动化）

### boss（xx直聘）

**boss_adb.py**

> 基于【adb命令】实现自动化爬取，解析页面xml提取岗位信息，需要APP打开搜索岗位列表页后再运行脚本

**boss_spider.py**

> 基于【pyppeteer】实现自动化爬取xpath解析页面提取岗位信息，直接运行即可

**data_wash.py**

> 对爬取到的数据进行清洗，并生成Excel文件

### mt（美团）

**sssf.py**

> 美团小游戏【谁是首富】孤岛求生自动跳桥脚本

**sssf_all_auto.py**

> 美团小游戏【谁是首富】日常任务脚本

**sssf_spring.py**

> 美团小游戏【谁是首富】春节自动对对联脚本

**town_auto.py**

> 美团小镇自动投骰子脚本

## company（公司项目提高开发效率）

**fetch_api_table_data.py**

> 提取接口Wiki里的表格参数，转换输出：var 字段名: 类型? = null,

**generate_mock_data.py**

> 根据 Kotlin实体类代码 生成用于Mock的Response Data数据，使用方法如下：把Kotlin实体类的代码贴到【Kotlin实体类.txt】文件中，引用到的类型也要包含。然后直接生成json数据，json解析异常一般是漏了引用到的实体类，或者没有继承Serializable接口

**generate_widget_object_by_xml.py**

> 根据xml布局，生成Kotlin中可以直接调用的控件对象 (需要支持DataBinding)

## markdown（Markdown相关）

### md_to_wx（将md文件生成带特定样式的微信公号文章html）

> 简单用法：把md文件丢到article/md目录下，运行app.py即可在article/out目录下生成html文件。 具体开发过程及使用方法可查阅：[hzwz-markdown](markdown/md_to_wx/README.md)

### transform（md文件转换）

**md_transform.py**

> md文件本地化（就是图片下载到本地，修改原有图片指向），生成doc。使用方法：

> 将要转换的md文件放到 origin_md 目录下，然后运行即可自动转换。如果用到生成doc的功能，需要电脑先安装一下pandoc，下载地址：https://github.com/jgm/pandoc/releases

**zybl_xlsx_to_local_md.py**

> cmd markdown(作业部落) 数据备份xlsx文件 批量生成本地MD文件的脚本


### url_style_fix（url风格批量修正）

**app.py**

> 修正url风格，如：![][1] → ![](xxx)

## media（多媒体）

### download（视频下载）

**video_download.py**

> 视频下载，默认采用you_get下载，B站链接支持破解下载(requests或idm)

### subtitle_extract

**app.py**

> 字幕提取工具，代码还未完成迁移~


## spider（爬虫）

### mall（某小电商站点）

**mall_spider.py**

> 某小站点的爬取示例


## util（工具模块）

**adb_util.py**

> adb命令模块

**download_util.py**

> 下载模块

**file_util.py**

> 文件操作模块

**logger_util.py**

> 日志模块

**ocr_util.py**

> OCR文字识别模块

**os_util.py**

> 系统信息相关模块

**pic_util.py**

> 图片处理模块

**pyppeteer_utils.py**

> pyppeteer工具模块