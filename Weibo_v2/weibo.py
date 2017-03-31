# -*- coding: utf-8 -*-


import re
import urllib.request
from time import sleep
import requests
from bs4 import BeautifulSoup
from http.cookiejar import LWPCookieJar
import parsedate
from filter import Filter

COOKIE_FILE = 'cookiejar'
HOST = 'http://weibo.cn'
LOGIN_URL = 'http://login.weibo.cn/login/'


class Weibo:
    def __init__(self):
        session = requests.Session()
        session.cookies = LWPCookieJar(COOKIE_FILE)
        self.session = session
        self.session.cookies.load()

    def get_info(self, target, proxy, proxy_n):
        req = self.session.get(target, proxies={'http': 'http://%s' % (proxy[proxy_n])})
        soup = BeautifulSoup(req.text, 'lxml')
        data = dict()
        data['title'] = soup.title.string
        if soup.find_all('input', attrs={'name': 'mp'}):
            data['page'] = int(soup.find('input', attrs={'name': 'mp'}).get('value'))
        else:
            data['page'] = 0
        return data

    def fetch_content(self, uid, count, proxy, proxy_n):
        contentlist = []
        if count > 5:
            count = 5
        for i in range(1, count + 1):
            url = 'http://weibo.cn/%s?page=%d' % (uid, i)
            req = self.session.get(url)
            while req.status_code != 200:
                req = self.session.get(url, proxies={'http': 'http://%s' % (proxy[proxy_n])})
                print(req.status_code)
                proxy_n += 1
                if req.status_code == 200:
                    print('use proxy %s' % proxy[proxy_n])
                    break
                elif proxy_n == len(proxy):
                    print('proxy ip is useless')
                    break
            soup = BeautifulSoup(req.text, 'lxml')
            items = soup.find_all('div', 'c', id=True)
            for item in items:
                content = dict({'wb_id': '', 'content_id': '', 'content_url': '', 'content': '', 'pic': '', 'forward':
                                '', 'comment': '', 'like': '', 'type': '', 'from': '', 'pub_time': '', 'grab_time': ''})
                try:
                    content['uid'] = uid
                    if len(item.select('span.cmt')) > 0:
                        content['type'] = 2     # 转发微博  赞评论和转发数抓最后一个div
                    else:
                        content['type'] = 1
                    content['id'] = item.get('id').replace('M_', '')
                    content['url'] = 'http://weibo.com/' + uid + '/' + content['id']
                    time = item.select('span.ct')[0].get_text().split('\xa0来自')[0]
                    content['pub_time'] = parsedate.parse_date(time)
                    content['grab_time'] = parsedate.now_date()
                    if content['type'] == 2:
                        if len(item.find_all('div')) == 3:
                            at = item.find_all('div')[0].find_all('a')[0].get_text()
                            wb = item.select('div span.ctt')[0].get_text()
                            content['content'] = Filter.filteremoji((item.find_all('div')[2].get_text().replace('转发理由:', '').split("\xa0\xa0")[0] + '//@' + at + ':' + wb).replace('\"', '\''))
                            content['pic'] = item.find_all('div')[1].select(' > a')[1].get('href')
                            content['like'] = item.find_all('div')[2].select(' > a')[-4].get_text()[2:-1]
                            content['forward'] = item.find_all('div')[2].select(' > a')[-3].get_text()[3:-1]
                            content['comment'] = item.find_all('div')[2].select(' > a')[-2].get_text()[3:-1]
                            content['from'] = item.select('span.ct')[0].get_text().split('\xa0来自')[1]
                        elif len(item.find_all('div')) == 2:
                            at = item.find_all('div')[0].find_all('a')[0].get_text()
                            wb = item.select('div span.ctt')[0].get_text()
                            content['content'] = Filter.filteremoji((item.find_all('div')[1].get_text().split("  \xa0\xa0")[0] + '//@' + at + ':' + wb).replace('\"', '\''))
                            content['like'] = item.find_all('div')[1].select(' > a')[-4].get_text()[2:-1]
                            content['forward'] = item.find_all('div')[1].select(' > a')[-3].get_text()[3:-1]
                            content['comment'] = item.find_all('div')[1].select(' > a')[-2].get_text()[3:-1]
                            content['from'] = item.select('span.ct')[0].get_text().split('\xa0来自')[1]
                    elif content['type'] == 1:
                        content['content'] = Filter.filteremoji((item.find_all('span', attrs={'class': 'ctt'})[0].get_text()).replace('\"', '\''))
                        content['from'] = item.select('span.ct')[0].get_text().split('\xa0来自')[1]
                        if len(item.find_all('div')) == 2:
                            if len(item.find_all('div')[1].select(' > a')) > 0:
                                content['pic'] = item.find_all('div')[1].select(' > a')[-5].get('href')
                                content['like'] = item.find_all('div')[1].select(' > a')[-4].get_text()[2:-1]
                                content['forward'] = item.find_all('div')[1].select(' > a')[-3].get_text()[3:-1]
                                content['comment'] = item.find_all('div')[1].select(' > a')[-2].get_text()[3:-1]
                        elif len(item.find_all('div')) == 1:
                            content['like'] = item.find('div').select(' > a')[-4].get_text()[2:-1]
                            content['forward'] = item.find('div').select(' > a')[-3].get_text()[3:-1]
                            content['comment'] = item.find('div').select(' > a')[-2].get_text()[3:-1]
                    if i == 1 and item.select('span.kt'):
                        content['type'] = 3
                    contentlist.append(dict(content))
                except IndexError:
                    print(content)
            sleep(10)
        return contentlist

    def get_uid(self, name):
        uid = ''
        url = 'http://weibo.cn/search/user/?keyword=' + urllib.request.quote(name) + '&retcode=6102'
        req = self.session.get(url)
        soup = BeautifulSoup(req.text, 'lxml')
        items = soup.find_all('table')
        if len(items) == 0:
            print('no relatvie search info!')
        else:
            a = items[0].find_all(href=re.compile('attention'))
            if len(a) != 0:
                a[0].get('href')
                uid = re.findall(r'/attention/add\?uid=(.*?)&amp;rl', items[0].encode('utf8').decode(), re.S)
                print('%s' % uid[0])
        return uid

