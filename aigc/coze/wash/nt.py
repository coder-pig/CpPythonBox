import json
import requests_async
import re
import time

# 提取活动信息的正则
activity_pattern = re.compile(
    r'temprop="summary">(.*?)<.*?时间：</span>(.*?)<.*?<li title="(.*?)">.*?地点：<.*?费用：</span>(.*?)</strong>', re.S)


# 城市和区的Bean
class City:
    def __init__(self, name_cn, name_req_param, district_dict):
        self.name_cn = name_cn
        self.name_req_param = name_req_param
        self.district_dict = district_dict


# 发起请求
async def send_request(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Host": "www.douban.com",
        "Refer": url
    }
    # 请求响应结果
    response_data = await requests_async.get(url, headers=headers)
    # 提取响应结果中的活动信息
    match_results = activity_pattern.findall(response_data.text)
    result_str = ""
    for result in match_results:
        activity_name = result[0].replace("\n", "").strip() if result[0] else "暂无数据"
        activity_time = result[1].replace("\n", "").strip() if result[1] else "暂无数据"
        activity_address = result[2].replace("\n", "").strip() if result[3] else "暂无数据"
        activity_cost = result[3].replace("\n", "").strip().replace("<strong>", "") if result[3] else "暂无数据"
        result_str += "-【{}】| {} | {} | {}\n".format(activity_name, activity_cost, activity_time, activity_address)
    return result_str


async def main(args: Args) -> Output:
    # 城市和区的请求参数
    city_list = [
        City("深圳市", "shenzhen", {
            "罗湖区": 130288, "福田区": 130289, "南山区": 130290, "宝安区": 130291, "龙岗区": 130292,
            "盐田区": 130293, "坪山区": 131682, "龙华区": 131683, "光明区": 131691,
        }), City("广州市", "guangzhou", {
            "从化": 130277, "荔湾区": 130266, "越秀区": 130267, "海珠区": 130268, "天河区": 130269, "白云区": 130270,
            "黄埔区": 130271, "番禺区": 130272, "花都区": 130273, "南沙区": 130274, "萝岗区": 130275, "增城区": 130276
        }), City("上海市", "shanghai", {
            "黄浦区": 129242, "徐汇区": 129244, "长宁区": 129245, "静安区": 129246, "普陀区": 129247,
            "闸北区": 129248, "虹口区": 129249, "杨浦区": 129250, "闵行区": 129251, "宝山区": 129252,
            "嘉定区": 129253, "浦东新区": 129254, "金山区": 129255, "松江区": 129256, "青浦区": 129257,
            "奉贤区": 129259, "崇明县": 129260
        }), City("北京市", "beijing", {
            "东城区": 128519, "西城区": 128520, "朝阳区": 128523, "丰台区": 128524, "石景山区": 128525,
            "海淀区": 128526, "门头沟区": 128527, "房山区": 128528, "通州区": 128529, "顺义区": 128530,
            "昌平区": 128531, "大兴区": 128532, "怀柔区": 128533, "平谷区": 128534, "密云县": 128535, "延庆县": 128536
        })
    ]
    # 活动类型参数
    category_dict = {
        "音乐": "music", "戏剧": "drama", "讲座": "salon", "聚会": "party", "电影": "film",
        "展览": "exhibition", "运动": "sports", "公益": "commonweal", "旅行": "travel",
        "赛事": "competition", "课程": "course", "亲子": "kids", "其它": "others"
    }
    params = args.params
    input_json = json.loads(params["input"])
    request_url = "https://www.douban.com/location/{}/events/weekend"
    for city in city_list:
        if city.name_cn == input_json['city']:
            # 拼接城市参数
            request_url = request_url.format(city.name_req_param)
            # 拼接活动类型参数
            if input_json['category'] is not None and len(input_json['category']) > 0:
                categoty_req_param = category_dict[input_json['category']]
                if category_dict:
                    categoty_req_param = categoty_req_param
                else:
                    categoty_req_param = "all"
            else:
                categoty_req_param = "all"
            request_url += "-{}".format(categoty_req_param)
            # 拼接区
            district = city.district_dict.get(input_json['district'])
            if district:
                request_url += "-{}".format(district)

    result_str = "为您检索到【{}-{}-{}】的周末活动信息：\n".format(
        input_json['city'], input_json['district'],
        input_json['category'] if len(input_json['category']) > 0 else "全部"
    )
    # 请求三次接口获取前三页数据，休眠0.5秒防封
    r1 = await send_request(request_url)
    time.sleep(0.5)
    r2 = await send_request(request_url + "?start=10")
    time.sleep(0.5)
    r3 = await send_request(request_url + "?start=20")
    result_str += r1
    result_str += r2
    result_str += r3
    ret: Output = {
        "result": result_str,
        "request_url": request_url,
        'r1': r1,
        'r2': r2,
        'r3': r3,
    }
    return ret
