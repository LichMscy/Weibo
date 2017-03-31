# -*-coding: utf-8 -*-

import re
import logging
import urllib.request
from time import sleep
import requests
from bs4 import BeautifulSoup
from util import parsedate
from util.filter import Filter

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s]%(name)s:%(levelname)s:%(message)s"
)


class Content:
    def __init__(self, cookies, proxies):
        session = requests.Session()
        self.session = session
        self.cookies = cookies
        self.proxies = proxies

    def getpagenum(self, target):
        req = self.session.get(target, cookies=self.cookies)
        soup = BeautifulSoup(req.text, 'lxml')
        data = dict()
        try:
            data['title'] = soup.title.string
            if soup.find_all('input', attrs={'name': 'mp'}):
                data['page'] = int(soup.find('input', attrs={'name': 'mp'}).get('value'))
            else:
                data['page'] = 0
        except AttributeError:
            data['title'] = ''
            data['page'] = 0
        return data

    def snatch(self, uid, count):
        contentlist = []
        if count > 5:
            count = 5
        for i in range(1, count + 1):
            url = 'http://weibo.cn/%s?page=%d' % (uid, i)
            req = self.session.get(url, cookies=self.cookies)
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
                time = item.select('span.ct')[0].get_text().split('\xa0来自')[0]
                content['pub_time'] = parsedate.parse_date(time)
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

    # def getuid(self, name):
        # uid = ''
        # headers = {
        #     'Host': 's.weibo.com',
        #     'Referer': 'http://s.weibo.com/?Refer=STopic_icon',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        #                   'Chrome/55.0.2883.87 Safari/537.36',
        #     'Cookie': '%s' % self.cookies,
        # }
        # url = 'http://s.weibo.com/user/' + urllib.request.quote(urllib.request.quote(name)) + '&Refer=SUer_box'
        # req = urllib.request.Request(url, headers=headers)
        # req.set_proxy(host=self.proxies['http'], type='http')
        # html = urllib.request.urlopen(req).read().decode()
        # raw = re.findall(r'\\u66fe\\u7528\\u540d', html, re.S)
        # if len(raw) != 0:
        #     url1 = 'http://s.weibo.com/user/&former=' + urllib.request.quote(urllib.request.quote(name))
        #     req1 = urllib.request.Request(url1, headers=headers)
        #     html1 = urllib.request.urlopen(req1).read().decode()
        #     uids = re.findall(r'''uid=\\"(.*?)\\"''', html1, re.S)
        #     return uids[0]
        #
        # reg2 = r'''<a\s{1}class=\\"W_texta\s{1}W_fb\\".*?uid=\\"(.*?)\\"[^>]+>\\n\\t.*?<em\s{1}class=\\"red\\">(.*?)<\\\/em>.*?\\n\\t\\t\\n\\t'''
        # raw1 = re.findall(reg2, html, re.S)
        # for rawi in raw1:
        #     s = rawi[1].encode('utf8').decode('unicode-escape')
        #     if s == name:
        #         return rawi[0]
        #     else:
        #         continue
        # return uid

    def snatch_wb_info(self, uid):
        dic = dict()
        url = 'http://weibo.cn/%s/info' % uid
        avatar_url = 'http://weibo.cn/%s/avatar?rl=0' % uid
        profile_url = 'http://weibo.cn/%s/profile?filter=1&page=1' % uid
        try:
            req = self.session.get(url, cookies=self.cookies)
            while req.status_code != 200:
                logging.warning('Snatch (Id:%s) failed' % uid)
                exit()
            soup = BeautifulSoup(req.text, 'lxml')
            dic['wb_id'] = uid
            dic['wb_url'] = 'http://weibo.com/u/%s' % uid
            dic['wb_name'] = ''.join(re.findall('昵称[：:]+(.*?)<', soup.extract().decode(), re.S))
            dic['sex'] = ''.join(re.findall('性别[：:]+(.*?)<', soup.extract().decode(), re.S))
            if dic['sex'] == '男':
                dic['sex'] = 1
            elif dic['sex'] == '女':
                dic['sex'] = 2
            else:
                dic['sex'] = 0
            dic['verify'] = ''.join(re.findall('认证[：:]+(.*?)<', soup.extract().decode(), re.S))
            dic['intro'] = ''.join(re.findall('简介[：:]+(.*?)<', soup.extract().decode(), re.S))
            dic['intro'] = Filter.filteremoji(dic['intro'])
            avatar_req = self.session.get(avatar_url, cookies=self.cookies)
            while avatar_req.status_code != 200:
                logging.warning('Snatch (Id:%s) failed' % uid)
                exit()
            avatar_soup = BeautifulSoup(avatar_req.text, 'lxml')
            div_c = avatar_soup.find_all('div', 'c')
            dic['avatar'] = ''
            if div_c:
                avatar_ele = div_c[0].select('img')
                if avatar_ele:
                    dic['avatar'] = ''.join(avatar_ele[0].get('src'))
                else:
                    logging.error('Fail to access the Avatar page!')
            dic['province'] = ''.join(re.findall('地区[：:]?(.*?)<', soup.extract().decode(), re.S))
            profile_req = self.session.get(profile_url, cookies=self.cookies)
            while profile_req.status_code != 200:
                logging.warning('Snatch (Id:%s) failed' % uid)
                exit()
            profile_soup = BeautifulSoup(profile_req.text, 'lxml')
            img = profile_soup.select('span.ctt > img')
            if img:
                img = img[0].get('src')
                if len(requests.get('http://vgirl.weibo.com/%s' % uid).history) == 0:
                    dic['verified'] = 4  # 微女郎认证
                elif img == 'http://h5.sinaimg.cn/upload/2016/05/26/319/5338.gif':
                    dic['verified'] = 1  # 红v认证
                elif img == 'http://h5.sinaimg.cn/upload/2016/05/26/319/5337.gif':
                    dic['verified'] = 2  # 蓝v认证
                elif img == 'http://h5.sinaimg.cn/upload/2016/05/26/319/5547.gif':
                    dic['verified'] = 3  # 微博达人认证
                else:
                    dic['verified'] = 0
            else:
                dic['verified'] = 0
            dic['wb_nums'] = ''.join(re.findall('微博\[(.*?)\]', profile_soup.extract().decode(), re.S))
            if dic['wb_nums'] == '':
                dic['wb_nums'] = 0
            dic['focus'] = ''.join(re.findall('关注\[(.*?)\]', profile_soup.extract().decode(), re.S))
            if dic['focus'] == '':
                dic['focus'] = 0
            dic['fans'] = ''.join(re.findall('粉丝\[(.*?)\]', profile_soup.extract().decode(), re.S))
            if dic['fans'] == '':
                dic['fans'] = 0
            dic['create_time'] = parsedate.now_date()
        except Exception as e:
            logging.error(e)
        return dic
