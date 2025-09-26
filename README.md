# 🐍 CpPythonBox

> 一个功能丰富的Python工具箱，包含自动化脚本、开发效率工具、数据处理、爬虫等多个实用模块 ✨

## 📋 项目概述

本项目是一个个人Python脚本合集，涵盖了日常开发和生活中的各种自动化需求：
- 🤖 自动化操作脚本（招聘、游戏等）
- 🛠️ 开发效率提升工具  
- 📝 Markdown文档处理工具链
- 🎥 多媒体内容处理
- 🕷️ 各类网站数据爬取
- 🔧 通用工具模块库

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 依赖包：详见各模块的requirements

### 配置文件
修改 `config.ini` 中的相关配置项：
```ini
[config]
# 视频字幕提取相关配置
video_subtitle_host = xxx
bd_ocr_app_id = xxx
bd_ocr_api_key = xxx

[openai]
openai_token = xxx
```

## 📁 项目结构

### 🤖 auto（自动化脚本）

#### boss（招聘网站自动化）
- **`boss_adb.py`** - 基于ADB命令的移动端自动化爬取，解析页面XML提取岗位信息
- **`boss_spider.py`** - 基于Pyppeteer的PC端自动化爬取，XPath解析页面数据  
- **`data_wash.py`** - 数据清洗工具，生成Excel分析报告

#### mt（美团小游戏自动化）
- **`sssf.py`** - 美团【谁是首富】孤岛求生自动跳桥脚本
- **`sssf_all_auto.py`** - 美团【谁是首富】日常任务自动化
- **`sssf_spring.py`** - 美团【谁是首富】春节对对联自动化
- **`town_auto.py`** - 美团小镇自动投骰子脚本

### 🛠️ company（开发效率工具）

- **`fetch_api_table_data.py`** - 提取接口文档表格参数，输出格式：`var 字段名: 类型? = null`
- **`generate_mock_data.py`** - 根据Kotlin实体类生成Mock测试数据（JSON格式）
- **`generate_widget_object_by_xml.py`** - 解析XML布局生成Kotlin控件对象代码（支持DataBinding）

### 📝 markdown（Markdown工具链）

#### backups（文档备份工具）
- **`yuque_md_local.py`** - 语雀文档批量导出为本地Markdown
- **`zybl_md_local.py`** - 作业部落文档备份工具
- **`backups_util.py`** - 通用备份工具类

#### md_to_wx（微信公众号转换）
- **`app.py`** - 将Markdown转换为微信公众号格式HTML
- **`styles_renderer.py`** - 样式渲染器，支持多种主题
- 📁 **styles/** - 预设样式模板库
- 📁 **template/** - HTML模板文件

#### transform（格式转换）
- **`md_transform.py`** - Markdown文件本地化（图片下载+链接修复）+ DOC格式导出

#### url_style_fix（链接格式修正）
- **`app.py`** - 批量修正Markdown中的图片链接格式
- **`auto_to_list.py`** - 自动生成目录列表

### 🎥 media（多媒体处理）

#### download（视频下载）
- **`video_download.py`** - 多平台视频下载器（支持you-get）
- **`bilibili_video_all_download_idm.py`** - B站多P视频批量下载（IDM加速）

#### subtitle_extract（字幕提取）
- **`jpav_cn_subtitle.py`** - 视频字幕提取工具
- **`xj_api.py`** - 字幕处理API接口

### 🕷️ spider（爬虫工具集）

#### apifox
- **`apifox.py`** - Apifox接口文档动态更新工具

#### edu（教育资源）
- **`xfz_spider.py`** - 自考题库数据爬取
- **`data_wash.py`** - 教育数据清洗

#### mall（电商数据）
- **`mall_spider.py`** - 电商网站商品信息爬取
- **`generate_category_file.py`** - 商品分类文件生成

#### music（音乐平台）  
- **`music_spider.py`** - 网易云音乐艺人粉丝数据爬取（含GUI界面）

### 🔧 util（通用工具库）

- **`adb_util.py`** - Android ADB命令封装
- **`download_util.py`** - 文件下载工具（支持多线程、断点续传）
- **`file_util.py`** - 文件操作工具集
- **`logger_util.py`** - 日志记录工具
- **`ocr_util.py`** - OCR文字识别（百度API）
- **`os_util.py`** - 系统信息获取
- **`pic_util.py`** - 图片处理工具
- **`proxy_util.py`** - 代理设置工具
- **`pyppeteer_utils.py`** - Pyppeteer浏览器自动化封装

## 🔧 安装与使用

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd CpPythonBox
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置设置**
   - 复制 `config.ini.example` 为 `config.ini`
   - 根据需要填写相关API密钥和配置项

4. **运行脚本**
   ```bash
   python auto/boss/boss_spider.py
   python markdown/md_to_wx/app.py
   ```

## 🎯 使用场景

- **求职场景**：自动爬取招聘信息，批量分析岗位数据
- **内容创作**：Markdown文档格式转换，微信公众号排版
- **数据收集**：各类网站信息爬取和数据分析
- **开发效率**：API文档处理，Mock数据生成
- **多媒体处理**：视频下载，字幕提取

## ⚠️ 注意事项

- 使用爬虫工具时请遵守网站robots.txt和相关法律法规
- 部分功能需要配置相应的API密钥
- 建议在虚拟环境中运行，避免依赖冲突

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件