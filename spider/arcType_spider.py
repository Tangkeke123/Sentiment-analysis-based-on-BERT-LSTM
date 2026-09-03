"""
    https://weibo.com/ajax/feed/allGroups
    微博类别信息爬取 存csv文件
"""
import csv
import os.path
import time
import numpy as np
import requests
import urllib3

# 禁用SSL警告（解决TLS/SSL连接重置问题）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def init_csv():
    """
    初始化操作，判断csv文件是否存在，不存在就创建一个
    """
    if not os.path.exists('arcType_data.csv'):
        with open('arcType_data.csv', 'w', encoding='utf8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                '类别标题(title)',
                '分组id(gid)',
                '分类id(containerid)'
            ])


def get_proxy():
    """
    获取代理IP配置
    """
    try:

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


def getJsonHtml(url, params, retries=5):
    """
    请求获取JSON数据，集成重试、代理、异常处理
    """
    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        'accept': 'application/json, text/plain, */*',
        'referer': 'https://weibo.com/',
        'origin': 'https://weibo.com',
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


def writeToCsv(row):
    """
    写入csv操作（追加）
    """
    with open('arcType_data.csv', 'a', encoding='utf8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)


def parseJson(json):
    """
    解析Json数据
    """
    try:
        arcTypeList = np.append(json['groups'][3]['group'], json['groups'][4]['group'])
        print(f"获取到 {len(arcTypeList)} 个分类")
        for arcType in arcTypeList:
            arcType_title = arcType['title']
            gid = arcType['gid']
            containerid = arcType['containerid']
            writeToCsv([arcType_title, gid, containerid])
        print("解析完成，已写入CSV")
    except Exception as e:
        print(f"解析JSON失败: {e}")


def start():
    init_csv()
    url = "https://weibo.com/ajax/feed/allGroups"
    jsonHtml = getJsonHtml(url, {})
    if jsonHtml:
        parseJson(jsonHtml)
        print("微博类别信息爬取成功")
    else:
        print("获取数据失败，请检查网络、代理或Cookie")


if __name__ == '__main__':
    start()
