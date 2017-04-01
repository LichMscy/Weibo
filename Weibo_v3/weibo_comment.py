# -*-coding: utf-8 -*-

import re
import logging
import requests
from proxypool import cookie

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s]%(name)s:%(levelname)s:%(message)s"
)


def comment(url, content, content_id, wb_id, t_cookie):
    session = requests.Session()
    param = {
        'srcuid':   wb_id,
        'id':       content_id,
        'rl':       1,
        'content':  content
    }
    header_cookie = ''
    for key, value in t_cookie.items():
        header_cookie += '{} = {}; '.format(key, value)
    headers = {
        'Cookie': header_cookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36'
    }
    # req = session.request(method='POST', url=url, data=param, cookies=t_cookie)
    req = session.request(method='POST', url=url, data=param, cookies=t_cookie, headers=headers)
    if len(re.findall('>操作失败<', req.text, re.S)) > 0:
        logging.warning('comment fail!')
    elif len(re.findall('>评论失败, repeat content! 页面返回中...<', req.text, re.S)) > 0:
        logging.warning('comment fail! repeat comment!')
    # print(req.text)


def forward(url, content, content_id, root):
    session = requests.Session()
    param = {
        'act': 'dort',
        'rl':   1,
        'id':   content_id,
        'content':      content,
        'rtkeepreason': 'on',
    }
    if root == 'rtcomment':             # forward with comment
        param['rtcomment'] = 'on'
    elif root == 'rtrootcomment':       # forward with comment to root post
        param['rtcomment'] = 'on'
        param['rtrootcomment'] = 'on'
    g = cookie.GetCookie(weibo_info={'usn': 'xxxxx', 'pwd': 'xxxxx'}, enable_proxy=False, proxies=[])
    cookie_dic = g.getcookies()
    req = session.request(method='POST', url=url, data=param, cookies=cookie_dic)
    print(req.text)


def like(content_id, wb_id):
    url = 'http://weibo.cn/attitude/%s/add?uid=%d&rl=1&gid=&st=eef502' % (content_id, wb_id)
    session = requests.Session()
    g = cookie.GetCookie(weibo_info={'usn': 'xxxxx', 'pwd': 'xxxxx'}, enable_proxy=False, proxies=[])
    cookie_dic = g.getcookies()
    req = session.request(method='GET', cookies=cookie_dic, url=url)
    print(req.text)


def unlike(content_id, wb_id):
    url = 'http://weibo.cn/attitude/%s/delete?uid=%d&rl=1&st=eef502' % (content_id, wb_id)
    session = requests.Session()
    g = cookie.GetCookie(weibo_info={'usn': 'xxxxx', 'pwd': 'xxxxx'}, enable_proxy=False, proxies=[])
    cookie_dic = g.getcookies()
    req = session.request(method='GET', url=url, cookies=cookie_dic)
    print(req.text)


# if __name__ == '__main__':
#     comment('http://weibo.cn/comments/addcomment?st=eef502', 'teeest', 'Ej4EP1SoG', xxxxx)    # comment weibo
    # forward('http://weibo.cn/repost/dort/Ej4EP1SoG?st=eef502', '转发微博', 'Ej4EP1SoG', '')     # forward weibo
    # forward('http://weibo.cn/repost/dort/Ej4EP1SoG?st=eef502', '转发微博', 'Ej4EP1SoG', 'rtcomment')    # forward weibo with comment
    # forward('http://weibo.cn/repost/dort/Ej4EP1SoG?st=eef502', '转发微博', 'Ej4EP1SoG', 'rtrootcomment')    # forward weibo with comment to root post
    # like('xxxxx', xxxxx)
    # unlike('xxxxx', xxxxx)

