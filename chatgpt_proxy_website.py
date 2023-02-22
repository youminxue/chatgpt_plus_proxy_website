# -*- coding: utf-8 -*-
'''
第一作者：cooolr
第二作者：chatgpt
日期：2023-02-22
'''

import os
import requests
from hashlib import md5
from urllib.parse import unquote
from flask import Flask, request, redirect, send_file, Response, stream_with_context
from werkzeug.routing import BaseConverter

proxies = {"https": ""}

# 定义Cookie参数
# 需要在cookie获取以下三个参数，_puid为plus会员专属，没它不行
_puid = ""
cf_clearance = ""
session_token = ""

# 请求头
headers = {
    'authority': 'chat.openai.com',
    'accept': 'text/event-stream',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'cookie': f'cf_clearance={cf_clearance}; __Secure-next-auth.session-token={session_token}; _puid={_puid}',
    'dnt': '1',
    'origin': 'https://chat.openai.com',
    'pragma': 'no-cache',
    'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}

def get_authorization():
    """获取 accessToken"""
    url = "https://chat.openai.com/api/auth/session"
    r = requests.get(url, headers=headers, proxies=proxies)
    authorization = r.json()["accessToken"]
    return "Bearer "+authorization

# 获取 accessToken 并设置到 headers 中
headers["authorization"] = get_authorization()

# 定义 Flask 应用程序
app = Flask(__name__)

# 自定义正则表达式转换器
class RegexConverter(BaseConverter):
    def __init__(self, map, *args):
        self.map = map
        self.regex = args[0]

# 注册正则表达式转换器
app.url_map.converters['regex'] = RegexConverter

# 将 cookie 存储到字典中
cookie_dict = {cookie.split("=")[0]: cookie.split("=")[1] for cookie in headers["cookie"].split("; ")}

# 创建存储资源的目录
resource_dir = './resource'
os.makedirs(resource_dir, exist_ok=True)

# 处理所有的 HTTP 请求方法
@app.route('/<path:uri>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'TRACE', 'CONNECT', 'PATCH'])
def index(uri):
    param = '&'.join([f'{i}={j}' for i,j in request.args.items()])
    url = f"https://chat.openai.com/{uri}?{param}" if param else f"https://chat.openai.com/{uri}"

    # 如果请求的是静态资源，优先从本地获取，否则从远程获取
    if any(x in url for x in ('.jpg', '.png', '.ico', '.woff', '.otf', '.css')):
        ext = url.split('.')[-1]
        filename = md5(url.encode('utf-8')).hexdigest()
        filepath = os.path.join(resource_dir, f'{filename}.{ext}')
        if os.path.isfile(filepath):
            # 如果本地存在该静态资源，则返回该资源
            return send_file(filepath)
        else:
            # 否则，从远程获取资源并保存到本地，再返回该资源
            r = requests.get(url, headers=headers, cookies=cookie_dict)
            with open(filepath, 'wb') as f:
                f.write(r.content)
            return send_file(filepath)
    elif 'conversation' in url:
        # 如果请求的是实时对话，则使用流式处理响应，提高效率
        r = requests.request(request.method, url, headers=headers, cookies=cookie_dict, data=request.data, proxies=proxies, stream=True)
        response = Response(stream_with_context(r.iter_content(chunk_size=1024)))
        response.headers['content-type'] = r.headers.get('content-type')
        return response
    else:
        # 对于其他请求，则使用常规方式处理
        r = requests.request(request.method, url, headers=headers, cookies=cookie_dict, data=request.data, proxies=proxies)
        return r.content.replace(b'https://chat.openai.com', b'http://127.0.0.1:8011')

if __name__ == "__main__":
    app.run(port=8011, threaded=True)
    # 在浏览器打开: http://127.0.0.1:8011/chat
