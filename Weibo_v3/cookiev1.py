# -*-coding: utf-8 -*-

import time
import logging
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s]%(name)s:%(levelname)s:%(message)s"
)

logger = logging.getLogger(__name__)
logging.getLogger("selenium").setLevel(logging.WARNING)  # 将selenium的日志级别设成WARNING，太烦人

IDENTIFY = 1  # 验证码输入方式:        1:看截图aa.png，手动输入     2:云打码
dcap = dict(DesiredCapabilities.PHANTOMJS)  # PhantomJS需要使用老版手机的user-agent，不然验证码会无法通过
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) "
    "Version/4.0 Mobile Safari/533.1 "
)


def get_cookies(weibo):
    account = weibo['usn']
    password = weibo['pwd']
    """ 获取一个账号的Cookie """
    #   local path refer phantomjs
    webdriver.Proxy('')
    browser = webdriver.PhantomJS(executable_path='xxxxx',
                                  desired_capabilities=dcap)
    try:
        browser.get("https://weibo.cn/login/")
        time.sleep(1)
        browser.save_screenshot("aa.png")

        failure = 0
        while "微博" in browser.title and failure < 5:
            failure += 1
            username = browser.find_element_by_name("mobile")
            username.clear()
            username.send_keys(account)

            psd = browser.find_element_by_xpath('//input[@type="password"]')
            psd.clear()
            psd.send_keys(password)
            try:
                code = browser.find_element_by_name("code")
                code.clear()
                if IDENTIFY == 1:
                    img = browser.find_element_by_xpath('//form[@method="post"]/div/img[@alt="请打开图片显示"]')
                    x = img.location["x"]
                    y = img.location["y"]
                    im = Image.open("aa.png")
                    im.crop((x, y, 100 + x, y + 22)).save("ab.png")  # 剪切出验证码
                    code_txt = input("请查看路径下新生成的aa.png，然后输入验证码:")  # 手动输入验证码
                else:
                    img = browser.find_element_by_xpath('//form[@method="post"]/div/img[@alt="请打开图片显示"]')
                    x = img.location["x"]
                    y = img.location["y"]
                    im = Image.open("aa.png")
                    im.crop((x, y, 100 + x, y + 22)).save("ab.png")  # 剪切出验证码
                    code_txt = yumdama.identify()  # 验证码打码平台识别
                code.send_keys(code_txt)
            except:
                pass

            commit = browser.find_element_by_name("submit")
            commit.click()
            time.sleep(3)
            if "我的首页" not in browser.title:
                time.sleep(4)

        cookie = {}
        if "我的首页" in browser.title:
            for elem in browser.get_cookies():
                cookie[elem["name"]] = elem["value"]
            logger.warning("Get Cookie Success!( Account:%s )" % account)
        return cookie
    except:
        logger.warning("Failed %s!" % account)
        exit()
    finally:
        try:
            browser.quit()
            logger.warning("Browser quited!")
        except:
            pass
