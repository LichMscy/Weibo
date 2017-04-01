# -*-coding: utf-8 -*-

import re
import time
import datetime
import logging
import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup
from util import parsedate
import persist_iics

logging.basicConfig(level=logging.INFO, format="[%(asctime)s]%(name)s:%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)
logging.getLogger("selenium").setLevel(logging.WARNING)


def init_phantomjs_driver():
    headers = {
        'Cookie': 'YF-Ugrow-G0=b02489d329584fca03ad6347fc915997; SUB=_2AkMvgPj2dcPxrAFYnPgWyGvkZYpH-jycVZEAAn7uJhMyOhgv7nBSqSVOKynW2PbhU4768kfRGZgNPwXeRA..; SUBP=0033WrSXqPxfM72wWs9jqgMF55529P9D9WWEFXHsNpvgJdQjr1GM.e765JpVF020SKM7e0571hMc',
    }
    for key, value in headers.items():
        webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value
    useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36'
    webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = useragent

    #   local path refer phantomjs
    driver = webdriver.PhantomJS(executable_path='xxxxx')
    driver.set_window_size(1366, 768)
    return driver


def update_cookies():
    p1 = persist_iics.Persist()
    accounts = p1.query_account()
    cookie = json.loads(accounts[0][3])
    req = requests.Session().get('http://weibo.cn/', cookies=cookie)
    if re.findall('登录|注册', req.text, re.S):
        logging.error('Account cookies out of date! (Account_id: %s)' % accounts[0][0])
        browser = init_phantomjs_driver()
        try:
            browser.get("http://weibo.com")
            time.sleep(3)
            failure = 0
            while "微博-随时随地发现新鲜事" == browser.title and failure < 5:
                failure += 1
                username = browser.find_element_by_name("username")
                pwd = browser.find_element_by_name("password")
                login_submit = browser.find_element_by_class_name('W_btn_a')
                username.clear()
                username.send_keys(accounts[0][1])
                pwd.clear()
                pwd.send_keys(accounts[0][2])
                login_submit.click()
                time.sleep(5)

                # if browser.find_element_by_class_name('verify').is_displayed():
                #     logger.error("Verify code is needed! (Account: %s)" % account)

            if "我的首页 微博-随时随地发现新鲜事" in browser.title:
                browser.get('http://weibo.cn/')
                cookies = dict()
                if "我的首页" in browser.title:
                    for elem in browser.get_cookies():
                        cookies[elem["name"]] = elem["value"]
                p2 = persist_iics.Persist()
                p2.save_account_cookies(accounts[0][0], cookies, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                logging.error('Account cookies updated! (Account_id: %s)' % accounts[0][0])
                return cookies
        except:
            logger.error("Weibo Login Unknown exception!")
            raise
    else:
        return cookie


def snatch_news_info(cookies):
    p1 = persist_iics.Persist()
    p1_result = p1.query_task()
    ids = re.findall('weibo.com/(.*?)/(.*?)[?]', p1_result[0][1], re.S)[0]
    if ids and ids[0] and ids[1]:
        url = 'http://weibo.cn/comment/{}?uid={}'.format(ids[1], ids[0])
        req = requests.get(url, cookies=cookies)
        while req.status_code != 200:
            logging.error('Snatch (Task_id: %s) failed!' % p1_result[0][0])
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
        create_time = soup.select('span.ct')[0].get_text().split('\xa0来自')[0]
        dic['create_time'] = parsedate.parse_date(create_time)
        p2 = persist_iics.Persist()
        p2.insert_news(dic)
        logging.info('Snatch wb news success! (Task_id: %s)' % p1_result[0][0])

    p3 = persist_iics.Persist()
    p3.update_task_status(p1_result[0][0])
    logging.error('Snatch (Task_id: %s) failed! Updated status!' % p1_result[0][0])


def comment_prepare():
    # TODO: query comment list from db.
    comment_list = tuple()

    p1 = persist_iics.Persist()
    result = p1.query_task()
    ids = re.findall('weibo.com/(.*?)/(.*?)[?]', result[0][1], re.S)[0]
    url = 'http://weibo.cn/comment/{}?uid={}'.format(ids[1], ids[0])
    result = dict()
    result['comment'] = comment_list
    result['url'] = url
    return result


def comment(weibo, wb_content, wb_comment_url):
    code = 1
    account = weibo['usn']
    password = weibo['pwd']
    # service_args = [
    #     '--proxy=127.0.0.1:9999',
    #     '--proxy-type=http',
    #     '--ignore-ssl-errors=true'
    # ]
    browser = init_phantomjs_driver()

    try:
        browser.get("http://weibo.com")
        time.sleep(3)
        # browser.save_screenshot("weibocom.png")
        failure = 0
        while "微博-随时随地发现新鲜事" == browser.title and failure < 5:
            failure += 1
            username = browser.find_element_by_name("username")
            pwd = browser.find_element_by_name("password")
            login_submit = browser.find_element_by_class_name('W_btn_a')
            username.clear()
            username.send_keys(account)
            pwd.clear()
            pwd.send_keys(password)
            login_submit.click()
            time.sleep(5)

            # if browser.find_element_by_class_name('verify').is_displayed():
            #     logger.error("Verify code is needed! (Account: %s)" % account)

        if "我的首页 微博-随时随地发现新鲜事" in browser.title:
            browser.get(wb_comment_url)
            comment_avatar = browser.find_element_by_xpath("//div/a[@href='http://weibo.com/']")
            comment_avatar.send_keys(Keys.TAB, wb_content)
            time.sleep(5)
            comment_submit = browser.find_element_by_xpath("//a[@class='W_btn_a']")
            comment_submit.click()
            time.sleep(5)
            code = 0
    except:
        logger.error("weibo comment Unknown exception!")
        raise
    return code

# if __name__ == '__main__':
#     print(comment({'usn': 'xxxxx', 'pwd': 'xxxxx'}, '死...死...死狗一', 'http://weibo.com/xxxxx/xxxxx'))
