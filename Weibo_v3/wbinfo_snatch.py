# -*-coding: utf-8-*-

import re
import json
import logging
import MySQLdb
import urllib.request
import requests
import persist
from bs4 import BeautifulSoup
from proxypool import cookie
from util import parsedate
from util.filter import Filter

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s]%(name)s:%(levelname)s:%(message)s"
)


def snatch_wb_info(uid, t_cookie):
    dic = dict()
    url = 'http://weibo.cn/%s/info' % uid
    avatar_url = 'http://weibo.cn/%s/avatar?rl=0' % uid
    profile_url = 'http://weibo.cn/%s/profile?filter=1&page=1' % uid
    try:
        req = requests.Session().get(url, cookies=t_cookie)
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
        avatar_req = requests.Session().get(avatar_url, cookies=t_cookie)
        while avatar_req.status_code != 200:
            logging.warning('Snatch (Id:%s) failed' % uid)
            exit()
        avatar_soup = BeautifulSoup(avatar_req.text, 'lxml')
        div_c = avatar_soup.find_all('div', 'c')
        if div_c:
            avatar_ele = div_c[0].select('img')
            if avatar_ele:
                dic['avatar'] = ''.join(avatar_ele[0].get('src'))
            else:
                logging.error('Fail to access the Avatar page!')
        dic['province'] = ''.join(re.findall('地区[：:]?(.*?)<', soup.extract().decode(), re.S))
        profile_req = requests.Session().get(profile_url, cookies=t_cookie)
        while profile_req.status_code != 200:
            logging.warning('Snatch (Id:%s) failed' % uid)
            exit()
        profile_soup = BeautifulSoup(profile_req.text, 'lxml')
        img = profile_soup.select('span.ctt > img')
        if img:
            img = img[0].get('src')
            if len(requests.get('http://vgirl.weibo.com/%s' % uid).history) == 0:
                dic['verified'] = 4     # 微女郎认证
            elif img == 'http://h5.sinaimg.cn/upload/2016/05/26/319/5338.gif':
                dic['verified'] = 1     # 红v认证
            elif img == 'http://h5.sinaimg.cn/upload/2016/05/26/319/5337.gif':
                dic['verified'] = 2    # 蓝v认证
            elif img == 'http://h5.sinaimg.cn/upload/2016/05/26/319/5547.gif':
                dic['verified'] = 3    # 微博达人认证
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


def main(uid, t_cookie, task_id):
    info = snatch_wb_info(uid, t_cookie)
    p = persist.Persist()
    p.save_wb_media_info(info)
    p.update_id_into_wb_task(info['wb_id'], task_id)
