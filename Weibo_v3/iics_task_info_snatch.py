# -*-coding: utf-8-*-

import re
import logging
import requests
import persist_iics
from snatch import cookie
from util import parsedate
from bs4 import BeautifulSoup
import cookiev2

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s]%(name)s:%(levelname)s:%(message)s"
)


def snatch_iics_info():
    p = persist_iics.Persist()
    result = p.query_task()
    ids = re.findall('weibo.com/(.*?)/(.*?)[?]', result[0][1], re.S)[0]
    if ids and ids[0] and ids[1]:
        g = cookie.GetCookie(weibo_info={'usn': 'xxxxx', 'pwd': 'xxxxx'}, enable_proxy=False, proxies=[])
        t_cookie = g.getcookies()
        url = 'http://weibo.cn/comment/{}?uid={}'.format(ids[1], ids[0])
        req = requests.get(url, cookies=t_cookie)
        while req.status_code != 200:
            logging.error('Snatch (Task: %s) failed!' % result[0][0])
            exit()
        soup = BeautifulSoup(req.text, 'lxml')
        item = soup.select('span.ctt')[0]
        dic = dict()
        dic['platform_id'] = 2
        dic['media_name'] = '新浪微博'
        dic['title'] = item.get_text()[1:23] + '...'
        dic['summary'] = item.get_text()[1:290]
        dic['src_url'] = result[0][1]
        dic['task_id'] = result[0][0]
        dic['comment_num'] = ''.join(re.findall('\">\s评论\[(.*?)\]\s<', soup.extract().decode(), re.S))
        like = re.findall('\">赞\[(.*?)\]<', soup.extract().decode(), re.S)
        if like:
            dic['like_num'] = like[0]
        dic['forward_num'] = ''.join(re.findall('\">转发\[(.*?)\]<', soup.extract().decode(), re.S))
        time = soup.select('span.ct')[0].get_text().split('\xa0来自')[0]
        dic['create_time'] = parsedate.parse_date(time)
        p1 = persist_iics.Persist()
        p1.insert_news(dic)
    p1 = persist_iics.Persist()
    clib_id = 1
    content_list = p1.query_comment(clib_id)


if __name__ == '__main__':
    snatch_iics_info()
