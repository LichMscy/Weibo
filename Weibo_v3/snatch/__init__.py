# -*-coding: utf-8-*-
import re
import threading
import logging
from time import sleep
from snatch import content
from proxypool import cookie
import persist
import requests

local_object = threading.local()
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s]%(name)s:%(levelname)s:%(message)s"
)


def process_request():
    no = local_object.no
    # task begin, query task info
    p1 = persist.Persist()
    infos = p1.select_raw_info(1*no)
    c = content.Content(local_object.cookie, local_object.proxy)
    for info in infos:
        uid = str(info['wb_id'])
        url = 'http://weibo.cn/%s' % uid
        data = c.getpagenum(url)
        if data['title'] != '':
            logging.info('Get cookie success! (Thread-%s)' % no)
            contents = c.snatch(uid, data['page'])
            # save weibo content to db
            p2 = persist.Persist()
            for con in contents:
                p2.save_content(con)
            p2.conn.close()
            # update task status
            p3 = persist.Persist()
            p3.save_patch_task_status(info['id'])
            # save task info to table `wb_media`
            user_info = c.snatch_wb_info(uid)
            p4 = persist.Persist()
            p4.save_wb_media_info(user_info)
            p4.conn.close()
            logging.info('Spider-Thread No.%s sleeping...' % no)
            sleep(720)
        else:
            logging.error('Spider-Thread No.%s useless' % no)
            exit()


def process_thread(proxy, t_cookie, no):
    local_object.no = no
    local_object.proxy = proxy
    local_object.cookie = t_cookie
    process_request()

if __name__ == '__main__':
    t = list()
    weibo_list = [
        {'usn': 'xxxxx', 'pwd': 'xxxxx'},
        {'usn': 'xxxxx', 'pwd': 'abc123456'},
        {'usn': 'xxxxx', 'pwd': 'abc123456'},
    ]
    p = persist.Persist()
    proxylist = p.selectproxy()
    for weibo_info in weibo_list:
        for i in range(0, len(proxylist)):
            g = cookie.GetCookie(weibo_info=weibo_info, enable_proxy=True, proxies=proxylist[i])
            cookielist = g.getcookies()
            th = threading.Thread(target=process_thread, args=(proxylist[i], cookielist, i), name='Thread-%d' % i)
            t.append(th)
    for thread in t:
        thread.start()
    for thread in t:
        thread.join()
