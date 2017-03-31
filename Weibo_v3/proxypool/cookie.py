# -*-coding: utf-8 -*-

import json
import base64
import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s]%(name)s:%(levelname)s:%(message)s"
)


class GetCookie:
    def __init__(self, weibo_info, enable_proxy, proxies):
        self.weibo = weibo_info
        self.session = requests.Session()
        if enable_proxy:
            self.session.proxies = proxies

    def getcookies(self):
        url = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
        account = self.weibo['usn']
        passwd = self.weibo['pwd']
        username = base64.b64encode(account.encode('utf-8')).decode('utf-8')
        postdata = {
            'entry': 'sso',
            'gateway': '1',
            'from': 'null',
            'savestate': '30',
            'useticket': '0',
            'pagerefer': '',
            'vsnf': '1',
            'su': username,
            'service': 'sso',
            'sp': passwd,
            'sr': '1440*900',
            'encoding': 'UTF-8',
            'cdult': '3',
            'domain': 'sina.com.cn',
            'prelt': '0',
            'returntype': 'TEXT',
        }
        session = self.session
        r = session.post(url, data=postdata)
        jsonstr = r.content.decode('gbk')
        cookie = json.loads(jsonstr)
        if cookie['retcode'] == '0':
            cookie = session.cookies.get_dict()
        else:
            logging.error('Get cookie Failed!')
            exit()
        return cookie
