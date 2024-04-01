import re

from util.file_util import read_file_text_content

activity_pattern = re.compile(
    r'temprop="summary">(.*?)<.*?时间：</span>(.*?)<.*?<li title="(.*?)">.*?地点：<.*?费用：</span>(.*?)</strong>', re.S)

if __name__ == '__main__':
    content = read_file_text_content("test.html")
    match_results = activity_pattern.findall(content)
    result_str = ""
    for result in match_results:
        activity_name = result[0].replace("\n", "").strip() if result[0] else "暂无数据"
        activity_time = result[1].replace("\n", "").strip() if result[1] else "暂无数据"
        activity_address = result[2].replace("\n", "").strip() if result[3] else "暂无数据"
        activity_cost = result[3].replace("\n", "").strip().replace("<strong>", "") if result[3] else "暂无数据"
        result_str += "-【{}】| {} | {} | {}\n".format(activity_name, activity_cost, activity_time, activity_address)
    print(result_str)
