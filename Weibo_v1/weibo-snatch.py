# -*-coding:utf8-*-
import sys
import string
import math
from time import sleep
import re
import json
import os
import urllib.request
from bs4 import BeautifulSoup
import requests
from lxml import etree
import MySQLdb

from mysqlconfig import url
from mysqlconfig import name

headers = {
    'Host': 's.weibo.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/55.0.2883.75 Safari/537.36',
    'Referer': 'http://s.weibo.com/?Refer=STopic_icon',
    'Cookie': 'xxxxx',
}
cookie = {"Cookie":"xxxxx"}

conn = MySQLdb.connect(
    host="xxxxx",
    port=3306,
    user="xxxxx",
    passwd="xxxxx",
    database="xxxxx",
    charset='utf8',
)

cur = conn.cursor()

values = []
value = {
    'wb_id': "",
    'wb_url': "",
    'wb_name': "",
    'wb_former': "",
    'sex': "",
    'verify': "",
    'focus': "",
    'fans': "",
    'wb_nums': "",
    'fans_sex_p': "",
    'intro': "",
    'avatar': "",
    'province': "",
    'city': "",
    'kind': "",
    'verified': "",
    'level': "",
    'status': "",
    'create_time': "",
}
for i in range(1, int(math.floor(len(name)/10) + 2)):
    for j in range(10*(i-1), 10*i):
        print('Starting snatch %s' % name[j])
        value1 = value.copy()
        link = 'http://s.weibo.com/user/' + urllib.parse.quote(urllib.parse.quote(name[j])) + '&Refer=index'
        try:
            while value1['wb_id'] == "":
                source = urllib.request.Request(link, headers=headers)
                html = urllib.request.urlopen(source).read().decode('utf8')
                reg = r'user_feed_\w+_name'
                n = len(re.findall(reg, html, re.S))
                if n == 0:
                    print('Cookie out of date')
                    break
                for k in range(1, n + 1):
                    reg0 = 'user_feed_' + str(k) + r'_name\\">\\n\\t<em class=\'red\' usercard=\'id=(.*?)\'>(.*?)<\\/em>\\n\\t\\t\\n\\t<\\/a>'
                    reg1 = 'user_feed_' + str(k) + r'_url\\">(.*?)<\\/a>'
                    reg2 = r'person_reason\\"><span class=\\"related\\"><em>\\u66fe\\u7528\\u540d<a class=\\"W_linkb\\" href=\\"&former=' + urllib.parse.quote(urllib.parse.quote(name[j])) + r'\\">(.*?)<\\\/a><\\\/em>'
                    reg3 = r'uid=\\"(.*?)\\" suda-data=\\"key=tblog_search_user&value=user_feed_' + str(k) + r'_name\\">(.*?)<\\/a>'
                    reg4 = 'user_feed_' + str(k) + '_name(.*?)user_feed_' + str(k + 1)
                    reg5 = 'person_name(.*?)person_addr'
                    weibo_ele = re.findall(reg0, html, re.S)
                    weibo_url = re.findall(reg1, html, re.S)
                    html1 = re.findall(reg4, html, re.S)            # 截取每个搜索结果各部分数据
                    html2 = re.findall(reg5, html, re.S)            # 截取各个搜索结果各部分中的username,uid信息
                    if len(html1):
                        former = re.findall(reg2, html1[0], re.S)
                    if len(weibo_ele) == 0:
                        print(html)
                        print('Not Found!')
                    elif len(weibo_ele) == 1 and len(weibo_ele[0]) == 2:
                        if weibo_ele[0][1] == json.dumps(name[j]).replace('\"', ''):
                            value1['wb_id'] = weibo_ele[0][0]
                            value1['wb_url'] = weibo_url[0].replace('\\', '')
                            value1['wb_name'] = weibo_ele[0][1].encode('utf8').decode('unicode-escape')
                            values.append(dict(value1))
                            break
                        elif len(former) != 0 and former[0].encode('utf8').decode('unicode-escape') == name[j]:
                            if len(html2[k - 1]) > 0:
                                weibo_ele = re.findall(reg3, html2[k - 1], re.S)
                                value1['wb_id'] = weibo_ele[0][0]
                                value1['wb_url'] = weibo_url[0].replace('\\', '')
                                value1['wb_name'] = "".join(re.compile(r'[\u4e00-\u9fa5]+').findall(weibo_ele[0][1].encode('utf8').decode('unicode-escape')))
                                value1['wb_former'] = name[j]
                                values.append(dict(value1))
                                break
            print(value1)
        except IndexError:
            print('Snatch fail!')
        sleep(1)
    print('UserName snatch success!')

    for dic in values:
        url = 'http://weibo.cn/%s' % dic['wb_id']
        print(url)

        try:
            html = requests.get(url, cookies=cookie).content
            req = etree.HTML(html)
        except:
            print('Cookie out of date!')
        v = req.xpath('//div[@class="ut"]/span/img/@src')
        if len(v) > 0:
            if v[0] == 'http://h5.sinaimg.cn/upload/2016/05/26/319/5338.gif':
                dic['verified'] = 1        # 红v认证
            elif v[0] == 'http://h5.sinaimg.cn/upload/2016/05/26/319/5337.gif':
                dic['verified'] = 2        # 蓝v认证
        else:
            dic['verified'] = 0            # 无v认证
        element = req.xpath('//div[@class="ut"]/span[@class="ctt"]')
        dic['avatar'] = req.xpath('//img[@class="por"]/../img/@src')[0]
        part1 = element[0].xpath('string(.)').replace(" ", "").split("\xa0")
        if len(part1) == 3:
            if part1[1].split("/")[0] == '男':
                dic['sex'] = 1
            elif part1[1].split("/")[0] == 'nv':
                dic['sex'] = 2
            else:
                dic['sex'] = 0
            dic['province'] = part1[1].split("/")[1]
        if dic['verified'] == 0:
            dic['intro'] = element[1].xpath('string(.)')
        else:
            if len(element) == 3:
                dic['verify'] = element[1].xpath('string(.)').replace("认证：", "")
                dic['intro'] = element[2].xpath('string(.)')
            elif len(element) == 2:
                dic['intro'] = element[1].xpath('string(.)')
        part2 = req.xpath('//div[@class="tip2"]')[0].xpath('string(.)')
        dic['wb_nums'] = re.split('\[|\]', part2)[1]
        dic['focus'] = re.split('\[|\]', part2)[3]
        dic['fans'] = re.split('\[|\]', part2)[5]
        sql = "insert into wb_media(wb_id, wb_url, wb_name, sex, verify, focus, fans, wb_nums, intro, avatar, province, verified) " \
              "values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" \
              % (dic['wb_id'], dic['wb_url'], dic['wb_name'], dic['sex'], dic['verify'], dic['focus'], \
                 dic['fans'], dic['wb_nums'], dic['intro'], dic['avatar'], dic['province'], dic['verified'] )
        print(sql)
        try:
            cur.execute(sql)
            conn.commit()
        except:
            print('Insert fail!')
            conn.rollback()
    sleep(20)
conn.close()
