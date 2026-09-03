# proxy_util.py (请用此内容替换你原来的文件)
import requests
import random

# ====== 请替换为你成功测试的API信息 ======
# 用于提取代理IP的API接口（从你成功的测试代码中复制）
EXTRACT_API_URL = "https://dps.kdlapi.com/api/getdps/?secret_id=op13vs433rkv6nn8jf44&signature=tavu45omkz8qtk0gpr9p328tato9j1qa&num=1&sep=1"
# 私密代理的用户名密码认证（从你成功的测试代码中复制）
PROXY_USERNAME = "d2650939305"
PROXY_PASSWORD = "iaij0kfi"
# =======================================

# 可选：缓存代理IP，避免每次请求都调用API
_cached_proxy_ip = None


def get_a_proxy_ip():
    """从API提取一个代理IP"""
    global _cached_proxy_ip
    # 简单的缓存逻辑：如果已经有缓存的IP，就直接使用，不再请求API（可根据需要调整）
    if _cached_proxy_ip:
        return _cached_proxy_ip
    try:
        resp = requests.get(EXTRACT_API_URL, timeout=5)
        if resp.status_code == 200:
            # API返回的IP格式类似 "221.229.212.142:15875"
            proxy_ip = resp.text.strip()
            _cached_proxy_ip = proxy_ip
            return proxy_ip
        else:
            print(f"提取代理IP失败，状态码：{resp.status_code}")
            return None
    except Exception as e:
        print(f"提取代理IP异常：{e}")
        return None


def get_proxy_url():
    """构造带认证的完整代理URL，供requests的proxies参数使用"""
    proxy_ip = get_a_proxy_ip()
    if not proxy_ip:
        # 如果没有获取到IP，返回None，上层需要处理
        return None
    # 构造认证URL格式：http://用户名:密码@IP:端口
    proxy_url = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{proxy_ip}"
    return proxy_url


# 简单的自测
if __name__ == '__main__':
    url = get_proxy_url()
    print("生成的代理URL:", url)
    if url:
        proxies = {'http': url, 'https': url}
        try:
            r = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
            print("通过代理访问成功，返回IP:", r.json())
        except Exception as e:
            print("代理测试失败:", e)
