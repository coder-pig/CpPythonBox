// ==UserScript==
// @name         扣子插件工具信息爬取
// @namespace    http://tampermonkey.net/
// @version      2024-02-21
// @description  try to take over the world!
// @author       CoderPig
// @match        https://www.coze.cn/store/plugin
// @grant        GM_xmlhttpRequest
// @grant        GM_download
// ==/UserScript==

(function () {
    'use strict';
    console.log('插件加载...')

    // 浏览器跳转特定url
    function locationUrl(url) {
        window.location.href = url;
    }

    // 浏览器发起请求
    function sendRequest(url) {
        GM_xmlhttpRequest({
            method: "GET",
            url: url,
            onload: function (response) {
                console.log(response.responseText);
            }
        });
    }

    // 拦截url中有特定关键词的请求并下载响应内容
    function interceptAndSaveResponse(keyword) {
        var originalOpen = window.XMLHttpRequest.prototype.open;
        window.XMLHttpRequest.prototype.open = function () {
            if (arguments[1].includes(keyword)) {
                this.addEventListener('load', function () {
                    console.log('监听到请求', arguments[1]);
                    // 创建Blob块并获取该Blob对象的URL
                    var blob = new Blob([this.responseText], {type: 'application/json;charset=utf-8'});
                    var blobUrl = URL.createObjectURL(blob);
                    console.log('文件的url', blobUrl);
                    GM_download({
                        url: blobUrl,
                        name: "response.json",
                        saveAs: false,
                        onerror: function (error) {
                            //下载错误回调
                            console.log(error)
                        },
                        onprogress: (pro) => {
                            //如果此下载取得了一些进展，则要执行的回调
                            console.log(pro.loaded) //文件加载量
                            console.log(pro.totalSize) //文件总大小
                        },
                        ontimeout: () => {
                            //如果此下载由于超时而失败，则要执行的回调
                        },
                        onload: () => {
                            URL.revokeObjectURL(blobUrl);
                        }
                    });
                    // 下载完释放URL避免内存泄露

                }, false);
            }
            return originalOpen.apply(this, arguments);
        };
    }

    // 提取所有工作流信息，结果返回txt文件，Bot名-插件名-插件id-插件描述
    function fetchAllWorkFlowInfo() {
        const botInfoArray = ["7337223627307401231-工作规划大师", "7332475242608246821-新春萌宠大拜年", "7332511402818846755-龙年守护灵", "7332899804240150562-东北大哥拜年啦", "7332511402818666531-龙年限量盲盒", "7332907205143953442-我是一只龙", "7326151847062945818-旅游大师", "7334216846788558860-逼婚大挑战", "7330080702177787941-春联大王", "7331804785265475618-相亲模拟器(女生版)", "7325774753346650139-看图讲故事", "7330496997293752359-卡通头像", "7330306326565830682-米其林星探", "7327691806693490724-简历诊断", "7330217698355544115-小红书文案输出大师", "7329855229166600204-马歇尔音箱粉丝", "7330292680737423411-求职助手", "7329857057623031847-MBTI性格专家", "7328607141122670626-快递查询助手", "7328364654592573467-书法老师", "7326166527584157746-公司分析助手", "7330144269849886747-穿越二次元", "7332430138480607247-本子上的游戏", "7326604198378831923-数学老师", "7330070214572392485-周报不用写", "7330144975906258995-SWOT专家", "7330144975906422835-山顶洞人", "7328609700545855523-小冒险家", "7328709492403634191-购车小帮手", "7325772186130874418-论文搜索助手", "7328064633946816563-图书旅人", "7328749946491076642-天蓬元帅猪八戒", "7326127566006468617-健康饮食", "7326149183642140709-尾尾小阿姨", "7325782706489491482-足球大师", "7325765993006006282-占星师"]
        const resultArray = [];
        const botId = botInfoArray[0].split("-")[0]
        window.XMLHttpRequest.prototype.open = function () {
            if (arguments[1].includes("draftbot/get_bot_info")) {
                this.addEventListener('load', function () {
                    console.log('监听到请求', arguments[1]);
                    // 创建Blob块并获取该Blob对象的URL
                    var blob = new Blob([this.responseText], {type: 'application/json;charset=utf-8'});
                    var blobUrl = URL.createObjectURL(blob);
                    console.log('文件的url', blobUrl);
                    GM_download({
                        url: blobUrl,
                        name: "response.json",
                        saveAs: false,
                    });
                    // 下载完释放URL避免内存泄露

                }, false);
            }
            return originalOpen.apply(this, arguments);
        };
        window.location.href = `https://www.coze.cn/explore/${botId}`
        var originalOpen = window.XMLHttpRequest.prototype.open;

    }

    const botUrls = ["https://www.coze.cn/explore/7337223627307401231", "https://www.coze.cn/explore/7332475242608246821", "https://www.coze.cn/explore/7332511402818846755", "https://www.coze.cn/explore/7332899804240150562", "https://www.coze.cn/explore/7332511402818666531", "https://www.coze.cn/explore/7332907205143953442", "https://www.coze.cn/explore/7326151847062945818", "https://www.coze.cn/explore/7334216846788558860", "https://www.coze.cn/explore/7330080702177787941", "https://www.coze.cn/explore/7331804785265475618", "https://www.coze.cn/explore/7325774753346650139", "https://www.coze.cn/explore/7330496997293752359", "https://www.coze.cn/explore/7330306326565830682", "https://www.coze.cn/explore/7327691806693490724", "https://www.coze.cn/explore/7330217698355544115", "https://www.coze.cn/explore/7329855229166600204", "https://www.coze.cn/explore/7330292680737423411", "https://www.coze.cn/explore/7329857057623031847", "https://www.coze.cn/explore/7328607141122670626", "https://www.coze.cn/explore/7328364654592573467", "https://www.coze.cn/explore/7326166527584157746", "https://www.coze.cn/explore/7330144269849886747", "https://www.coze.cn/explore/7332430138480607247", "https://www.coze.cn/explore/7326604198378831923", "https://www.coze.cn/explore/7330070214572392485", "https://www.coze.cn/explore/7330144975906258995", "https://www.coze.cn/explore/7330144975906422835", "https://www.coze.cn/explore/7328609700545855523", "https://www.coze.cn/explore/7328709492403634191", "https://www.coze.cn/explore/7325772186130874418", "https://www.coze.cn/explore/7328064633946816563", "https://www.coze.cn/explore/7328749946491076642", "https://www.coze.cn/explore/7326127566006468617", "https://www.coze.cn/explore/7326149183642140709", "https://www.coze.cn/explore/7325782706489491482", "https://www.coze.cn/explore/7325765993006006282"]

    fetchAllWorkFlowInfo()
//interceptAndSaveResponse("explore/get_explore_list")


// 脚本加载后3s调用
//     setTimeout(function() {
//         locationUrl("https://juejin.cn/");
//     }, 1000);

})
();