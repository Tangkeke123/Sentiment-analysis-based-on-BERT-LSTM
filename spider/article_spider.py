"""
    微博内容爬取，以及存csv文件
    https://weibo.com/ajax/feed/hottimeline?group_id=1028032222&containerid=102803_2222&extparam=discover%7Cnew_feed
"""
import csv
import os
import time
from datetime import datetime
import requests
import urllib3
from util.stringUtil import clean_string

# 禁用SSL警告（解决TLS/SSL连接重置问题）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_proxy():
    """
    获取代理IP配置（使用已验证成功的快代理信息）
    """
    try:
        # 使用你测试成功的API密钥（请确保有效）
        api_url = "https://dps.kdlapi.com/api/getdps/?secret_id=op13vs433rkv6nn8jf44&signature=tavu45omkz8qtk0gpr9p328tato9j1qa&num=1&sep=1"

        # 获取代理IP
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            proxy_ip = response.text.strip()
            print(f"获取到代理IP: {proxy_ip}")

            # 用户名密码认证（使用你测试成功的账号）
            username = "d2650939305"
            password = "iaij0kfi"
            proxies = {
                "http": f"http://{username}:{password}@{proxy_ip}/",
                "https": f"http://{username}:{password}@{proxy_ip}/"
            }
            return proxies
        else:
            print(f"获取代理IP失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"获取代理IP异常: {e}")
        return None


def init_csv():
    """
    初始化操作，判断csv文件是否存在，不存在就创建一个
    """
    if not os.path.exists('article_data.csv'):
        with open('article_data.csv', 'w', encoding='utf8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'id',  # 帖子id
                'text_raw',  # 内容
                'reposts_count',  # 转发总数
                'comments_count',  # 评论总数
                'attitudes_count',  # 点赞总数
                'region_name',  # 发布位置 少部分没有这个值
                'created_at',  # 创建日期
                'articleType',  # 帖子类型
                'articleUrl',  # 帖子地址
                'authorId',  # 用户id
                'authorName',  # 用户名称
                'authorHomeUrl'  # 用户主页地址
            ])


def getJsonHtml(url, params, retries=5):
    """
    请求获取JSON数据，集成重试、代理、异常处理
    """
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        'accept': 'application/json, text/plain, */*',
        'referer': 'https://weibo.com/',
        'origin': 'https://weibo.com',
        # 使用最新有效的Cookie（从arcType_spider中复制，已验证成功）
        'cookie': "SCF=AvhOezVK5Atlp4_8mdTQtLxVEe0ZnItalsOq6CwhnxZEeTrRL16YfixTEEBfSg9bTWSUjqDEIAkXKV2dx3V7dZc.; WEIBOCN_FROM=1110005030; MLOGIN=0; _T_WM=29908206666; SUB=_2AkMe4Hn-f8NxqwFRm_kdxWvkboV-ww7EieKovIglJRM3HRl-yT9kqnUDtRB6NWBXEcSLultQs6N4Ov6t2RFmospm5LBs; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9W53JBrs_9b1Z3BNyg1-_-.G; XSRF-TOKEN=ca3b97; mweibo_short_token=414f811f8a; M_WEIBOCN_PARAMS=launchid%3D10000360-page_H5%26oid%3D5247488236980954%26luicode%3D10000011%26lfid%3D1076033144744040%26fid%3D1005053144744040%26uicode%3D10000011"
    }

    for attempt in range(1, retries + 1):
        try:
            # 每次重试重新获取代理（避免IP被封）
            proxies = get_proxy()
            print(f"第{attempt}次尝试，使用代理: {proxies is not None}")

            # 发送请求（若proxies为None则使用本机IP）
            response = requests.get(
                url,
                headers=headers,
                params=params,
                proxies=proxies,
                timeout=20,
                verify=False  # 解决SSL错误
            )

            print(f"请求状态码: {response.status_code}")

            if response.status_code == 200:
                return response.json()
            else:
                print(f"请求失败，状态码：{response.status_code}，响应内容：{response.text[:200]}")

        except requests.exceptions.ProxyError as e:
            print(f"代理错误: {e}，尝试直接连接...")
            # 代理失败时降级为直连
            try:
                response = requests.get(url, headers=headers, params=params, timeout=20, verify=False)
                if response.status_code == 200:
                    return response.json()
            except Exception as e2:
                print(f"直接连接也失败: {e2}")

        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")

        except Exception as e:
            print(f"未知异常: {e}")

        # 重试前等待（递增等待时间）
        if attempt < retries:
            wait_time = 2 * attempt  # 2, 4, 6, 8, 10...
            print(f"等待{wait_time}秒后重试...")
            time.sleep(wait_time)

    print(f"已重试{retries}次，仍然失败，返回None")
    return None


def getAllTypeList():
    """
    获取所有微博类别信息
    """
    allTypeList = []
    with open('arcType_data.csv', 'r', encoding='utf8', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过表头
        for articleType in reader:
            allTypeList.append(articleType)
    return allTypeList


def writeToCsv(row):
    """
    写入csv操作（追加）
    """
    with open('article_data.csv', 'a', encoding='utf8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)


def parseJson(json, articleType):
    """
    解析Json数据
    """
    articleList = json['statuses']
    for article in articleList:
        id = article['id']
        text_raw = clean_string(article['text_raw'])
        reposts_count = article['reposts_count']
        comments_count = article['comments_count']
        attitudes_count = article['reposts_count']  # 注意：这里应该用attitudes_count，但原代码用了reposts_count，保持原样
        region_name = article.get('region_name', '发布于').replace('发布于', '').strip()
        created_at = datetime.strptime(article['created_at'], "%a %b %d %H:%M:%S %z %Y").strftime("%Y-%m-%d %H:%M:%S")
        articleUrl = 'https://weibo.com/%s/%s' % (article['user']['id'], article['mblogid'])
        authorId = article['user']['id']
        authorName = article['user']['screen_name']
        authorHomeUrl = 'https://weibo.com/u/%s' % article['user']['id']

        writeToCsv([
            id,
            text_raw,
            reposts_count,
            comments_count,
            attitudes_count,
            region_name,
            created_at,
            articleType,
            articleUrl,
            authorId,
            authorName,
            authorHomeUrl
        ])


def start():
    url = 'https://weibo.com/ajax/feed/hottimeline'
    init_csv()
    allTypeList = getAllTypeList()
    print(allTypeList)
    print("微博内容爬取开始")
    for articleType in allTypeList:
        print('正在爬取类型为：【%s】的微博数据' % articleType[0])
        time.sleep(1)  # 每个分类之间间隔1秒
        params = {
            'group_id': articleType[1],
            'containerid': articleType[2],
            'extparam': 'discover|new_feed'
        }
        jsonHtml = getJsonHtml(url, params)

        if jsonHtml:
            parseJson(jsonHtml, articleType[0])
        else:
            print(f"获取类型【{articleType[0]}】的数据失败，已跳过")

    print("微博内容爬取结束")


if __name__ == '__main__':
    start()
