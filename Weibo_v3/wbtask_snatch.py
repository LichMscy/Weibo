# -*-coding: utf-8-*-

import logging
import re
import MySQLdb
import requests
import urllib.request
import persist
import time
from time import sleep
from bs4 import BeautifulSoup
from proxypool import cookie
from util import parsedate
from util.filter import Filter
import wbinfo_snatch

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s]%(name)s:%(levelname)s:%(message)s"
)


def getpagenum(target, t_cookie):
    req = requests.Session().get(target, cookies=t_cookie)
    soup = BeautifulSoup(req.text, 'lxml')
    data = dict()
    try:
        data['title'] = soup.title.string
        if soup.find_all('input', attrs={'name': 'mp'}):
            data['page'] = int(soup.find('input', attrs={'name': 'mp'}).get('value'))
    except AttributeError:
        data['title'] = ''
        data['page'] = 0
    return data


def snatch(uid, count, t_cookie):
    contentlist = []
    if count > 5:
        count = 5
    for i in range(1, count + 1):
        url = 'http://weibo.cn/%s?page=%d' % (uid, i)
        req = requests.Session().get(url, cookies=t_cookie)
        while req.status_code != 200:
            logging.error('Snatch ( Id:%s) failed!' % uid)
            exit()
        soup = BeautifulSoup(req.text, 'lxml')
        items = soup.find_all('div', 'c', id=True)
        for item in items:
            divs = item.find_all('div')
            content = dict({'uid': '', 'id': '', 'url': '', 'content': '', 'pic': '', 'forward': 0, 'comment': 0,
                            'like': 0, 'type': '', 'from': '', 'pub_time': '', 'grab_time': ''})
            content['uid'] = uid
            if re.findall('转发了\xa0', item.get_text(), re.S):
                content['type'] = 2
            else:
                content['type'] = 1
            content['id'] = item.get('id').replace('M_', '')
            content['url'] = 'http://weibo.com/' + uid + '/' + content['id']
            f_time = item.select('span.ct')[0].get_text().split('\xa0来自')[0]
            content['pub_time'] = parsedate.parse_date(f_time)
            content['grab_time'] = parsedate.now_date()
            if item.select('span.ct > a'):
                content['from'] = ''.join(re.findall('\xa0来自[^>]+>(.*?)</', item.extract().decode(), re.S))
            else:
                content['from'] = ''.join(re.findall('\xa0来自(.*?)</', item.extract().decode(), re.S))
            content['from'] = Filter.filteremoji(content['from'])
            like = re.findall('\">赞\[(.*?)\]<', item.extract().decode(), re.S)
            if like:
                content['like'] = like[-1]
            content['forward'] = ''.join(re.findall('\">转发\[(.*?)\]<', item.extract().decode(), re.S))
            content['comment'] = ''.join(re.findall('\">评论\[(.*?)\]<', item.extract().decode(), re.S))
            if content['type'] == 2:
                if len(divs) == 3:
                    at = divs[0].find_all('a')[0].get_text()
                    wb = item.select('div span.ctt')[0].get_text()
                    s = (divs[2].get_text().replace('转发理由:', '').split("\xa0\xa0")[0]
                         + '//@' + at + ':' + wb).replace('\"', '\'')
                    content['content'] = Filter.filteremoji(s)
                    content['pic'] = divs[1].select(' > a')[1].get('href')
                elif len(divs) == 2:
                    at = divs[0].find_all('a')[0].get_text()
                    wb = item.select('div span.ctt')[0].get_text()
                    s = (divs[1].get_text().split("\xa0\xa0")[0] + '//@' + at + ':' + wb).replace('\"', '\'')
                    content['content'] = Filter.filteremoji(s)
            elif content['type'] == 1:
                content['content'] = Filter.filteremoji(
                    (item.select('span.ctt')[0].get_text()).replace('\"', '\''))
                if len(divs) == 2:
                    if divs[1].select('a img'):
                        content['pic'] = divs[1].select('a img')[0].get('src')
            if i == 1 and item.select('span.kt'):
                content['type'] = 3
            contentlist.append(dict(content))
        sleep(10)
    return contentlist


def task_snatch():
    p1 = persist.Persist()
    result = p1.get_new_task()
    if result:
        g = cookie.GetCookie(weibo_info={'usn': 'xxxxx', 'pwd': 'xxxxx'}, enable_proxy=False, proxies=[])
        t_cookie = g.getcookies()
        for item in result:
            exist = ''
            correct = True
            uid = ''
            uid_s = re.findall('weibo.com\/(.*)', item[0], re.S)
            if uid_s:
                x = re.split('/|\?', uid_s[0])
                if x:
                    if x[0] == 'u':
                        x.remove('u')
                    uid_s = x[0]
                    url = 'http://weibo.cn/%s' % uid_s
                    req = requests.Session().get(url, cookies=t_cookie)
                    soup = BeautifulSoup(req.text, 'lxml')
                    uid = ''.join(re.findall('([\d]+)/(?=follow)', soup.extract().decode(), re.S))
                    info_url = 'http://weibo.cn/%s/info' % uid
                    info_req = requests.Session().get(info_url, cookies=t_cookie)
                    info_soup = BeautifulSoup(info_req.text, 'lxml')
                    wb_name = ''.join(re.findall('昵称[：:]+(.*?)<', info_soup.extract().decode(), re.S))
                    if wb_name != item[1]:
                        correct = False
            else:
                headers = {
                    'Host': 's.weibo.com',
                    'Referer': 'http://s.weibo.com/?Refer=STopic_icon',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/55.0.2883.87 Safari/537.36',
                }
                url = 'http://s.weibo.com/user/' + urllib.request.quote(urllib.request.quote(item[1])) + '&Refer=SUer_box'
                req = urllib.request.Request(url, headers=headers)
                html = urllib.request.urlopen(req).read().decode()
                raw = re.findall(r'\\u66fe\\u7528\\u540d', html, re.S)
                if len(raw) != 0:
                    url1 = 'http://s.weibo.com/user/&former=' + urllib.request.quote(urllib.request.quote(item[1]))
                    req1 = urllib.request.Request(url1, headers=headers)
                    html1 = urllib.request.urlopen(req1).read().decode()
                    uids = re.findall(r'''uid=\\"(.*?)\\"''', html1, re.S)
                    uid = uids[0]
                reg2 = r'''<a\s{1}class=\\"W_texta\s{1}W_fb\\".*?uid=\\"(.*?)\\"[^>]+>\\n\\t.*?<em\s{1}class=\\"red\\">(.*?)<\\\/em>.*?\\n\\t\\t\\n\\t'''
                raw1 = re.findall(reg2, html, re.S)
                for rawi in raw1:
                    s = rawi[1].encode('utf8').decode('unicode-escape')
                    if s == item[1]:
                        uid = rawi[0]
                        continue
                if uid == '':
                    p2 = persist.Persist()
                    p2.update_task_status(2, item[0], item[1])
                    continue
            p0 = persist.Persist()
            id_list = p0.select_wb_media_list()
            if not correct:
                p2 = persist.Persist()
                p2.update_task_status(2, item[0], item[1])
                logging.warning('Info(task_id: %s) incorrect!' % item[2])
                continue
            for tu in id_list:
                if uid == str(tu[0]):
                    p2 = persist.Persist()
                    p2.update_task_status(8, item[0], item[1])
                    exist = tu[0]
                    break
            if exist == '':
                wbinfo_snatch.main(uid, t_cookie, item[2])
                target = 'http://weibo.cn/%s' % uid
                data = getpagenum(target=target, t_cookie=t_cookie)
                if data['title'] != '':
                    contents = snatch(uid, data['page'], t_cookie)
                    p = persist.Persist()
                    for con in contents:
                        p.save_content(con)
                    p.conn.close()
                    logging.info('Snatch Success! (%s)' % item[1])
                    p2 = persist.Persist()
                    p2.update_task_status(8, item[0], item[1])
                else:
                    logging.warning('cookie out of date')
                    exit()
            else:
                p = persist.Persist()
                p.update_id_into_wb_task(uid, item[2])
                logging.info('Update task uid Success! (%s)' % item[1])

if __name__ == '__main__':
    logging.info('Snatch task running...')
    task_snatch()
    logging.info('Snatch task finish')
