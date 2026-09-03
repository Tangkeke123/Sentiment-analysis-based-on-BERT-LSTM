import requests

url = "https://weibo.com/ajax/feed/allGroups"
headers = {
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    'cookie': "SCF=AvhOezVK5Atlp4_8mdTQtLxVEe0ZnItalsOq6CwhnxZEeTrRL16YfixTEEBfSg9bTWSUjqDEIAkXKV2dx3V7dZc.; WEIBOCN_FROM=1110005030; MLOGIN=0; _T_WM=29908206666; SUB=_2AkMe4Hn-f8NxqwFRm_kdxWvkboV-ww7EieKovIglJRM3HRl-yT9kqnUDtRB6NWBXEcSLultQs6N4Ov6t2RFmospm5LBs; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9W53JBrs_9b1Z3BNyg1-_-.G; XSRF-TOKEN=ca3b97; mweibo_short_token=414f811f8a; M_WEIBOCN_PARAMS=launchid%3D10000360-page_H5%26oid%3D5247488236980954%26luicode%3D10000011%26lfid%3D1076033144744040%26fid%3D1005053144744040%26uicode%3D10000011",
    'referer': 'https://weibo.com/',
    'origin': 'https://weibo.com'
}
response = requests.get(url, headers=headers, timeout=10)
print("状态码:", response.status_code)
if response.status_code == 200:
    print("Cookie有效，数据获取成功！")
    print(response.json()['groups'][0]['title'])  # 打印第一个分组标题
else:
    print("失败，返回内容:", response.text)
