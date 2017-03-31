# -*-coding: utf-8 -*-

import re
import threading
import persist
import requests
import urllib.request
from time import sleep
from bs4 import BeautifulSoup
from proxypool import cookie

local_object = threading.local()


def process_info():
    p = persist.Persist()
    no = local_object.no
    items = p.select_raw_task_info(no*100)
    for item in items:
        uid = item[2].split('/')[-1]
        if uid:
            url = 'http://weibo.cn/%s' % uid
            req = requests.Session().get(url, cookies=local_object.cookie)
            soup = BeautifulSoup(req.text, 'lxml')
            uid = ''.join(re.findall('([\d]+)/(?=follow)', soup.extract().decode(), re.S))
            p1 = persist.Persist()
            p1.update_batch_task_status(item[0], uid, 1, 0)
        else:
            # parse dict type of cookie to string type
            # s = ''
            # for j in local_object.cookie.keys():
            #     s += str(j) + '=' + local_object.cookie[j] + ';'
            headers = {
                'Host': 's.weibo.com',
                'Referer': 'http://s.weibo.com/?Refer=STopic_icon',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
                # 'Cookie': s
            }
            request = urllib.request
            # set request proxy
            # proxy_support = request.ProxyHandler(local_object.proxy)
            # opener = request.build_opener(proxy_support)
            # request.install_opener(opener=opener)

            url = 'http://s.weibo.com/user/' + urllib.request.quote(urllib.request.quote(item[1])) + '&Refer=SUer_box'
            req = request.Request(url, headers=headers)
            html = request.urlopen(req).read().decode()
            raw = re.findall(r'\\u66fe\\u7528\\u540d', html, re.S)
            if len(raw) != 0:
                url1 = 'http://s.weibo.com/user/&former=' + urllib.request.quote(urllib.request.quote(item[1]))
                req1 = request.Request(url1, headers=headers)
                html1 = request.urlopen(req1).read().decode()
                uids = re.findall(r'''uid=\\"(.*?)\\"''', html1, re.S)
                if len(uids) != 0:
                    uid = uids[0]
                    p1 = persist.Persist()
                    p1.update_batch_task_status(item[0], uid, 1, 1)
            else:
                reg2 = r'''<a\s{1}class=\\"W_texta\s{1}W_fb\\".*?uid=\\"(.*?)\\"[^>]+>\\n\\t.*?<em\s{1}class=\\"red\\">(.*?)<\\\/em>.*?\\n\\t\\t\\n\\t'''
                raw1 = re.findall(reg2, html, re.S)
                for rawi in raw1:
                    match_name = rawi[1].encode('utf8').decode('unicode-escape')
                    if match_name == item[1]:
                        uid = rawi[0]
                        p1 = persist.Persist()
                        p1.update_batch_task_status(item[0], uid, 1, 0)
                        break
        sleep(10)


def process_thread(proxy, t_cookie, no):
    local_object.no = no
    local_object.proxy = proxy
    local_object.cookie = t_cookie
    process_info()


if __name__ == '__main__':
    weibo_info = [
        {'usn': 'xxxxx', 'pwd': 'abc123456'},
        {'usn': 'xxxxx', 'pwd': 'abc123456'},
    ]
    t = list()
    threads = list()
    p0 = persist.Persist()
    proxy_list = p0.selectproxy()
    for i in range(0, len(weibo_info)):
        # s = ''
        d = dict()
        g = cookie.GetCookie(weibo_info=weibo_info[i], enable_proxy=True, proxies=proxy_list[i])
        d['cookie'] = g.getcookies()
        d['proxy'] = proxy_list[i]
        t.append(d)
    for ii in range(0, len(t)):
        th = threading.Thread(target=process_thread, args=(t[ii]['proxy'], t[ii]['cookie'], ii), name='Thread-%d' % ii)
        threads.append(th)
        threads[ii].start()
    for iii in range(0, len(t)):
        threads[iii].join()
