#  -*-coding:utf8-*-
import re
import string
import sys
import os
import urllib.request
from bs4 import BeautifulSoup
import requests
from lxml import etree
# reload(sys)
# sys.setdefaultencoding('utf-8')

raw_uid = [1810269923]
cookie = {"Cookie": "xxxxx"}
for user_id in raw_uid:
    int_uid = int(user_id)
    print('Starting snatch %d' % int_uid)
    url = 'http://weibo.cn/u/%d?filter=0&page=1' % int_uid
    html = requests.get(url, cookies=cookie).content
    selector = etree.HTML(html)
    pageNum = 3
    result = ""
    urllist_set = set()
    word_count = 1
    # image_count = 1
    print(u'爬虫准备就绪...')

    for page in range(1, pageNum + 1):

        url = 'http://weibo.cn/u/%d?filter=0&page=%d' % (int_uid, page)
        lxml = requests.get(url, cookies=cookie).content

        selector = etree.HTML(lxml)
        content = selector.xpath('//span[@class="ctt"]')
        for each in content:
            text = each.xpath('string(.)')
            if word_count >= 4:
                text = "%d :" % (word_count - 3) + text + "\n \n "
            else:
                text = text + "\n \n "
            result = result + text
            word_count += 1
        fo = open("%s" % int_uid, "wb")
        fo.write(result.encode())
        word_path = os.getcwd() + '/%d' % int_uid
        print(u'微博账号：%d的文字微博爬取完毕' % int_uid)
