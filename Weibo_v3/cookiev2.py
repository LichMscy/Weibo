# -*-coding: utf-8 -*-

import time
import logging
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s]%(name)s:%(levelname)s:%(message)s"
)

logger = logging.getLogger(__name__)
logging.getLogger("selenium").setLevel(logging.WARNING)


def init_phantomjs_driver():
    headers = {
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        # 'Accept-Encoding': 'gzip, deflate, sdch',
        # 'Accept-Language':  'zh-CN,zh;q=0.8,en;q=0.6,und;q=0.4',
        # 'Cache-Control': 'no-cache',
        # 'Connection': 'keep-alive',
        # 'Host': 'weibo.com',
        'Cookie': '',   # 未登录时weibo.com的cookie
        # 'Pragma': 'no-cache',
        # 'Upgrade-Insecure-Requests':    1
    }
    for key, value in headers.items():
        webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value

    useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36 '
    webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = useragent

    #   local path refer phantomjs
    driver = webdriver.PhantomJS(executable_path='xxxxx')

    driver.set_window_size(1366, 768)
    return driver


def get_cookies(weibo):
    account = weibo['usn']
    password = weibo['pwd']
    service_args = [
        '--proxy=127.0.0.1:9999',
        '--proxy-type=http',
        '--ignore-ssl-errors=true'
    ]

    browser = init_phantomjs_driver()

    # try:
    browser.get("http://weibo.com/")
    time.sleep(3)
    browser.save_screenshot("weibocom.png")

    failure = 0
    while "微博-随时随地发现新鲜事" == browser.title and failure < 5:
        failure += 1
        username = browser.find_element_by_name('username')
        username.clear()
        username.send_keys(account)
        pwd = browser.find_element_by_name('password')
        pwd.clear()
        pwd.send_keys(password)

        commit = browser.find_element_by_class_name('W_btn_a')
        commit.click()
        time.sleep(5)

        # if browser.find_element_by_class_name('code').is_displayed():
        #     logger.error("Verify code is needed! (Account: %s)" % account)
        #     exit()

    # cookie = dict()
    if "我的首页 微博-随时随地发现新鲜事" in browser.title:

        #   weibo.cn get cookies
        # browser.get("http://weibo.cn/comment/Ej4EP1SoG")
        # time.sleep(5)
        # browser.save_screenshot("weibocncomment.png")
        # if "评论列表" in browser.title:
        #     for elem in browser.get_cookies():
        #         cookie[elem['name']] = elem['value']
        #     logger.warning("Getting cookies success! (Account: %s)" % account)
        # else:
        #     logger.warning("Getting cookies failed! (Account: %s)" % account)

        #   weibo.com comment textarea input
        browser.get("http://weibo.com/xxxxx/xxxxx")
        comment_avatar = browser.find_element_by_xpath("//div/a[@href='http://weibo.com/']")
        comment_textarea = comment_avatar.send_keys(Keys.TAB, "厉害了我的哥")
        time.sleep(5)
        browser.save_screenshot('weibocommenttextarea.png')
        comment_submit = browser.find_element_by_xpath("//a[@class='W_btn_a']")
        comment_submit.click()
        time.sleep(5)
        browser.save_screenshot('weibocommentsubmit.png')

if __name__ == '__main__':
    get_cookies({'usn': 'xxxxx', 'pwd': 'xxxxx'})
