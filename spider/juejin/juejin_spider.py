# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : juejin_spider.py
   Author   : CoderPig
   date     : 2024-03-13 10:14
   Desc     : 
-------------------------------------------------
"""
import re
import time

import requests as r


def fetch_tags_list():
    resp = r.post("https://api.juejin.cn/tag_api/v1/query_tag_list",
                  json={
                      "cursor": "0",
                      "key_word": "",
                      "limit": 10,
                      "sort_type": 1
                  })
    print(resp.text)


def fetch_article_list():
    resp = r.post("https://api.juejin.cn/content_api/v1/article/query_list",
                  json={"user_id": "xxx", "sort_type": 2, "cursor": "0"})
    print(resp.text)


# 用户信息类
class UserInfo:
    def __init__(self, user_name=None, description=None, register_time=None, follower_count=None,
                 post_article_count=None, got_digg_count=None, got_view_count=None, article_list=None):
        self.user_name = user_name
        self.description = description
        self.register_time = register_time
        self.follower_count = follower_count
        self.post_article_count = post_article_count
        self.got_digg_count = got_digg_count
        self.got_view_count = got_view_count
        self.article_list = article_list if article_list else []

    def __str__(self):
        return "作者名：{}，作者描述：{}，注册时间：{}，粉丝数：{}，文章数：{}，获得点赞数：{}，获得阅读数：{}，文章列表：{}".format(
            self.user_name, self.description, self.register_time, self.follower_count, self.post_article_count,
            self.got_digg_count, self.got_view_count, self.article_list)

    def to_json(self):
        return {
            "user_name": self.user_name,
            "description": self.description,
            "register_time": self.register_time,
            "follower_count": self.follower_count,
            "post_article_count": self.post_article_count,
            "got_digg_count": self.got_digg_count,
            "got_view_count": self.got_view_count,
            "article_list": [article.to_json() for article in self.article_list]
        }


# 提取输入url中的用户信息
def fetch_user_info(user_url):
    # 获取作者名的正则
    author_name_pattern = re.compile(r'<title>(.*?) 的个人主页', re.S)
    # 请求用户主页
    resp = r.get(user_url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/58.0.3029.110 Safari/537.3"})
    content = resp.text
    # 提取作者名称
    author_result = author_name_pattern.search(content)
    if author_result:
        # 获取作者名
        user_name = author_result.group(1)
        # 拼接获取用户信息的正则
        user_info_patter_str = r'user_name:"{}".*?'.format(
            user_name) + r'description:"(.*?)",.*?register_time:(\d+).*?follower_count:(\d+),post_article_count:(' \
                         r'\d+).*?got_digg_count:(\d+),got_view_count:(\d+).*?jpower:(\d+)'
        user_info_pattern = re.compile(user_info_patter_str, re.S)
        # 提取匹配的用户信息，只要第一个匹配结果
        results = user_info_pattern.findall(content)
        if results and len(results) > 0:
            user_info = UserInfo()
            user_info.user_name = user_name
            user_info.description = results[0][0]
            user_info.register_time = results[0][1]
            user_info.follower_count = results[0][2]
            user_info.post_article_count = results[0][3]
            user_info.got_digg_count = results[0][4]
            user_info.got_view_count = results[0][5]
            return user_info


# 文章信息类
class ArticleInfo:
    def __init__(self, title=None, brief_content=None, view_count=0, collect_count=0, digg_count=0,
                 comment_count=0, tags=None, link_url=None):
        self.title = title
        self.brief_content = brief_content
        self.view_count = view_count
        self.collect_count = collect_count
        self.digg_count = digg_count
        self.comment_count = comment_count
        self.tags = tags
        self.link_url = link_url

    def __str__(self):
        return "文章标题：{}，文章简介：{}，阅读数：{}，收藏数：{}，点赞数：{}，评论数：{}，标签：{}，文章链接：{}".format(
            self.title, self.brief_content, self.view_count, self.collect_count, self.digg_count, self.comment_count,
            self.tags, self.link_url)

    def to_json(self):
        return {
            "title": self.title,
            "brief_content": self.brief_content,
            "view_count": self.view_count,
            "collect_count": self.collect_count,
            "digg_count": self.digg_count,
            "comment_count": self.comment_count,
            "tags": self.tags if self.tags else [],
            "link_url": self.link_url
        }


# 爬取作者的文章列表
def fetch_author_article_infos(user_url):
    # 正则提取下user_id
    user_id_result = re.search(r"(\d+)", user_url)
    if user_id_result:
        user_id = user_id_result.group(1)
        cursor = 0
        article_info_list = []
        while True:
            time.sleep(2)
            request_json = {"user_id": user_id, "sort_type": 2, "cursor": str(cursor)}
            resp = r.post("https://api.juejin.cn/content_api/v1/article/query_list", headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/58.0.3029.110 Safari/537.3"
            }, json={"user_id": user_id, "sort_type": 2, "cursor": str(cursor)})
            print(resp.url, request_json)
            if resp:
                article_info = resp.json()
                if article_info and article_info["data"]:
                    for article in article_info["data"]:
                        article_info_list.append(
                            ArticleInfo(title=article["article_info"]["title"],
                                        brief_content=article["article_info"]["brief_content"],
                                        view_count=article["article_info"]["view_count"],
                                        collect_count=article["article_info"]["collect_count"],
                                        digg_count=article["article_info"]["digg_count"],
                                        comment_count=article["article_info"]["comment_count"],
                                        tags=list(map(lambda x: x["tag_name"], article["tags"])),
                                        link_url="https://juejin.im/post/" + article["article_id"]))
                    if len(article_info["data"]) < 10:
                        break
                    else:
                        cursor += 10
                    for info in article_info_list:
                        print(info)
                else:
                    break
            else:
                break
        return article_info_list


if __name__ == '__main__':
    test_list = ['前端', '后端', 'JavaScript', '面试', 'GitHub', 'Vue.js', '架构', '算法', 'Java', 'CSS', '代码规范',
                 'Node.js', '数据库', '程序员', '前端框架', '设计模式', 'React.js', 'HTML', 'Android', 'Linux',
                 '微信小程序', 'Python', 'Git', 'MySQL', 'Webpack', '开源', '人工智能', '设计', 'HTTP', '产品',
                 'ECMAScript 6', 'iOS', 'Redis', '全栈', 'Nginx', 'Docker', '微信', '机器学习', '正则表达式', 'Google',
                 'Chrome', '黑客', 'jQuery', 'Spring', '响应式设计', '编程语言', 'APP', 'React Native', 'Go', '命令行',
                 'Android Studio', '创业', 'Angular.js', 'TypeScript', '产品经理', 'Mac', '数据可视化', 'Vuex',
                 'Bootstrap', '深度学习', '操作系统', 'Apple', 'PHP', 'Photoshop', '安全', 'API', '微服务', 'MongoDB',
                 '图片资源', '阿里巴巴', 'Spring Boot', '数据挖掘', '运维', '源码', 'Canvas', 'Sublime Text', '设计师',
                 'gradle', '爬虫', 'Visual Studio Code', '招聘', 'Swift', 'C++', 'MVVM', 'Material Design', '云计算',
                 '敏捷开发', 'Markdown', 'NPM', 'Xcode', '物联网', 'Flutter', 'RxJava', '动效', 'HTTPS', '腾讯', 'JVM',
                 'Objective-C', '数据结构', '字体', '浏览器', '性能优化', '运营', 'JSON', '测试', 'Ajax', 'Icon',
                 '数据分析', 'SQL', 'MyBatis', 'LeetCode', '虚拟现实', 'Redux', 'DOM', '电子书', 'Vite', 'Debug',
                 'Kotlin', 'Ubuntu', 'Eclipse', '掘金翻译计划', '负载均衡', 'Spring Cloud', 'Promise', 'maven', 'SCSS',
                 '分布式', '配色', 'vue-router', '游戏', 'Sketch', 'Elasticsearch', '大数据', 'C', 'Kubernetes',
                 'IntelliJ IDEA', 'SVG', '函数式编程', '区块链', 'Element', 'VIM', 'Apache', 'Windows', 'Kafka',
                 'Facebook', 'ECharts', 'uni-app', '神经网络', '支付宝', 'axios', '计算机视觉', '稀土', 'SEO',
                 'Java EE', 'Unity3D', 'TCP/IP', 'TensorFlow', 'three.js', 'WebGL', 'Express', '单元测试', '响应式编程',
                 'Microsoft', '增强现实', 'Gulp', 'Hadoop', 'SQLite', 'WebSocket', 'Tomcat', '远程工作', '服务器',
                 '网络协议', '嵌入式', 'Firefox', '求职', 'Electron', 'APK', 'Django', '机器人', '投资', 'Webkit',
                 '编译器', 'NoSQL', '比特币', 'RabbitMQ', 'Atom', 'MVC', 'RocketMQ', '百度', 'ChatGPT', 'Shell', '科幻',
                 'ZooKeeper', 'Dubbo', 'flexbox', '连续集成', '云原生', 'CentOS', 'Netty', '消息队列', '容器', 'Spark',
                 'GitLab', 'V2EX', 'd3.js', 'Postman', 'Less', '掘金日报', 'UI Kit', 'Safari', '交互设计', '.NET',
                 'NLP', 'Laravel', 'PostgreSQL', 'Twitter', 'Weex', 'ORM', 'SSH', 'Wireshark', 'Rust', 'Jenkins',
                 'Ruby', 'UML', 'Sea.js', 'macOS', 'ESLint', 'JetBrains', 'Babel', '如何当个好爸爸', 'ionic', 'koa',
                 '音视频开发', '状态机', 'Grunt', '搜索引擎', '线下活动', 'Oracle', '掘金技术征文', '直播', 'SVN',
                 'Flask', '增长黑客', 'Hacker News', 'Ant Design', 'PostCSS', 'CDN', 'DNS', 'Scala', 'Backbone.js',
                 '小程序·云开发', 'C#', '沸点', 'Lua', '笔记', 'Flux', '视觉设计', 'OpenAI', 'MVP', 'Retrofit',
                 '树莓派', 'OKHttp', 'PyCharm', 'CMS', 'GraphQL', '游戏开发', 'ECMAScript 8', '逆向', 'Yarn', 'Medium',
                 '掘金·日新计划', 'ReactiveX', 'Android Jetpack', '年终总结', '排序算法', 'V8', 'Apple Watch',
                 'Underscore.js', 'DNodeJS', 'Web Components', '午夜话题', 'WebAssembly', 'Cocoa', '自动化运维',
                 'Instagram', 'Meteor.js', 'OpenCV', 'WebRTC', 'PyTorch', 'Excel', '源码阅读', 'Flink', '汇编语言',
                 'Keynote', 'Android Wear', 'Uber', 'SaaS', '掘金社区', 'RxJS', 'CoffeeScript', '资讯', 'iView',
                 '七牛云', 'ThinkPHP', 'Dart', 'Swagger', 'Ember.js', 'Bower', 'WebP', '图像识别', '掘金·金石计划',
                 '强化学习', 'Zepto.js', 'AB测试', 'LLVM', 'Egg.js', 'HBase', 'XSS', '蓝牙', 'mpvue', 'JUnit',
                 'HarmonyOS', 'IPython', '监控', 'fir.im', 'Nuxt.js', 'RequireJS', '团队管理', 'AIGC', 'PhpStorm',
                 'WeUI', 'Chart.js', 'Shiro', 'Rails', 'OpenGL', 'ReactiveCocoa', 'WWDC', 'Surge', 'GPT', 'SAMSUNG',
                 '以太坊', 'Trello', 'RxSwift', 'LaTex', 'CTO', '低代码', 'Hibernate', '数学', 'Travis CI', '图形学',
                 'DaoCloud', 'PWA', '编译原理', '计算机图形学', 'FFmpeg', 'SwiftUI', '自动驾驶', 'PyQt', 'Slack',
                 'VirtualBox', 'EventBus', 'NestJS', 'Hexo', 'Apache Hive', 'Solr', 'Arduino', 'iTerm', 'gRPC',
                 'Y Combinator', 'Glide', 'Amazon', 'NumPy', 'Apache ActiveMQ', 'WordPress', 'MariaDB', 'MATLAB',
                 'Memcached', 'Core ML', 'HDFS', 'ARKit', '莆田', 'Dagger', 'JMeter', 'Vonic', 'Workflow', '360',
                 'Gson', 'Fiddler', 'Scrapy', 'Polymer', 'Serverless', '数字货币', 'RESTful', '播客', '领域驱动设计',
                 '王者荣耀', 'C语言', 'Curl', 'Cocos2d-x', 'CircleCI', '5G', 'OpenStack', 'Cython', 'pandas', 'Axure',
                 'Pixate', 'Fastjson', '客户端', 'CI/CD', 'HTTP3', 'Taro', 'PhantomJS', 'Charles', 'Qt', 'Apache Log4j',
                 'HotFix', 'Elm', 'Picasso', 'Google IO', 'Emacs', 'Unicode', 'Yii', 'Lucene', 'AWS', 'Kibana',
                 'Selenium', 'Apache Storm', 'PM2', 'protobuf', '华为', 'Cordova', 'Realm', '智能合约', 'Vant',
                 'bpython', 'Tornado', '快应用', 'R', 'Groovy', 'MobX', '智能小程序', 'etcd', 'Linkedin', 'Swoole',
                 'RSS', 'DevOps', 'Logstash', 'Touch bar', 'rollup.js', 'Firebase', 'web.py', 'DBA', 'LLM', '边缘计算',
                 'NVIDIA', 'Grafana', 'KVM', 'VuePress', 'AndroidAnnotations', 'TiDB', '量子计算', 'Debian',
                 'Highlight.js', 'Airbnb', 'PyPy', 'Kaggle', 'NativeScript', 'greenDAO', 'Stylus', 'scikit-learn',
                 'RPC', 'Apache Flume', 'ZeroMQ', 'FreeMarker', 'Elixir', 'Keras', 'Ansible', 'Composer',
                 'Apache Thrift', 'Jest', 'Volley', 'Caffe', 'SciPy', '计算机组成原理', 'Immutable.js', 'Akka', 'ZXing',
                 'ButterKnife', 'CocoaPods', 'Unreal Engine', 'Project Lombok', 'Apache Kylin', 'Mocha', 'Erlang',
                 'JCenter', 'GPU', 'GIS', 'Karma', 'AFNetworking', 'WebView', 'VisualVM', 'Perl', 'web3', 'Vagrant',
                 'Apache Cassandra', 'WebVR', 'PhoneGap', 'Apache Mesos', 'JSPatch', 'Tinker', 'LeakCanary', 'WebStorm',
                 'Yeoman', 'deno', 'Swarm', 'Lisp', '掘金圆桌', '无人机', '有赞', 'SDWebImage', 'Preact', 'Haskell',
                 'Daydream', 'LevelDB', 'pyspider', '青训营笔记', 'Fresco', 'Service Mesh', 'Apache Ant', 'Fedora',
                 'SonarQube', 'Gevent', 'SymPy', 'Bluebird.js', 'Raft', 'Browserify', 'Gunicorn', 'Clojure', 'uWSGI',
                 'MPAndroidChart', '芯片', 'Jieba', 'Istio', 'Snapchat', 'Xposed', 'E2E', 'AMP', 'Omi', 'NSQ',
                 'Mockito', 'Twisted', 'Brython', 'Bintray', 'Fluentd', 'Android Things', 'Puppeteer', 'Symfony',
                 'Jekyll', 'Agera ', 'CasperJS', 'Unix', 'reCAPTCHA', 'QUnit', 'IndexedDB', 'Natural Language Toolkit',
                 'ORMLite', 'FMDB', 'Jasmine', 'ThinkJS', 'Alamofire', 'DeepStack', 'Jupyter', 'ReactOS', 'MJRefresh',
                 'SaltStack', 'Traefik', 'AsyncDisplayKit', 'marked', 'Gin', 'Fuchsia', 'fastlane', 'Mongoose',
                 'Monolog', 'Chrome OS', 'SnapKit', 'IGListKit', 'Perfect', 'Bulma', 'Caddy', 'Anko', 'Julia',
                 'Knockout', 'AChartEngine', 'Parcel', 'StatsD', 'Theano', 'Vapor', 'AIOps', 'ARCore', 'Polycode',
                 'libGDX', 'Feathers', 'mlpack', 'DroidMVP', 'Espresso', 'Phabricator', 'Solidity', 'Carthage',
                 'Classyshark', 'JitPack', 'Vuforia', 'AVA', 'RoboSpice', 'Stetho', 'FlatBuffers', '推广', 'GAN',
                 'MessagePack', 'Buck', 'Marko', 'Libratus', 'EazeGraph', 'DbInspector', 'RoboGuic', 'Fossil',
                 'Microsoft Edge', 'HTM', 'PyCon', 'RTC', 'Mozilla', 'Smartisan OS', 'FoundationDB', 'iPadOS', 'CMake',
                 'Svelte', 'mPaaS', 'NuGet', '笔记测评', '文心一言', 'Godot', '视频编码', '京东小程序', 'NEO', 'AMA',
                 'Midjourney', 'GWT', 'Chameleon', 'tvOS', 'Ramda', 'Libra', 'TLA+', '单片机', 'Sora', 'D', '百度飞桨',
                 'Debezium', 'greenplum', 'Visual Studio', 'SQL Server', 'Cocos Creator', 'Coze', 'visionOS', 'cesium',
                 'arco design', 'Modern.js', '抖音小程序', '轻服务', 'DALL-E3', 'Semi Design', 'Fes.js', 'Turbopack',
                 'Claude', '前端工程化', 'cpu', 'VitePress', 'Zabbix', 'bpmn-js', 'Gemini', 'w3cplus', 'Bun', 'Phaser',
                 'kerberos', 'mistral.ai', '工作流引擎']
    result = fetch_user_info("https://juejin.cn/user/3298190610663880/posts".replace("/posts", ""))

    # first_cursor_list = []
    # second_cursor_list = []
    # third_cursor_list = []
    # forth_cursor_list = []
    # post_article_count = int(int(result.post_article_count) / 10)
    # for pos in range(0, post_article_count):
    #     if pos % 4 == 0:
    #         first_cursor_list.append(str(pos * 10))
    #     elif pos % 4 == 1:
    #         second_cursor_list.append(str(pos * 10))
    #     elif pos % 4 == 2:
    #         third_cursor_list.append(str(pos * 10))
    #     else:
    #         forth_cursor_list.append(str(pos * 10))
    # print(first_cursor_list)
