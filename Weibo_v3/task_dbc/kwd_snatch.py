# -*- coding : utf-8 -*-

import re
import logging
import requests
import time
from task_dbc import persist
from util import parsedate
from util.filter import Filter
from bs4 import BeautifulSoup
import urllib.request
import weibo_auto_handle
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

logging.basicConfig(level=logging.INFO, format="[%(asctime)s]%(name)s:%(levelname)s:%(message)s")


def snatch_prepare():
    account = {'usn': 'xxxxx', 'pwd': 'xxxxx'}
    browser = weibo_auto_handle.init_phantomjs_driver()
    browser.get("http://weibo.com")
    time.sleep(3)
    failure = 0
    while "微博-随时随地发现新鲜事" == browser.title and failure < 5:
        failure += 1
        username = browser.find_element_by_name("username")
        pwd = browser.find_element_by_name("password")
        login_submit = browser.find_element_by_class_name('W_btn_a')
        username.clear()
        username.send_keys(account['usn'])
        pwd.clear()
        pwd.send_keys(account['pwd'])
        login_submit.click()
        time.sleep(5)

        # if browser.find_element_by_class_name('verify').is_displayed():
        #     logging.error("Verify code is needed! (Account: %s)" % account)

    if "我的首页 微博-随时随地发现新鲜事" in browser.title:
        browser.get('http://weibo.cn/')
        cookie = dict()
        if "我的首页" in browser.title:
            for elem in browser.get_cookies():
                cookie[elem["name"]] = elem["value"]
        # p2 = persist_iics.Persist()
        # p2.save_account_cookies(accounts[0][0], cookie, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        logging.error('Account cookies updated! (Account_id: %s)' % account['usn'])
        return cookie


def get_page_num(url, cookies):
    req = requests.Session().get(url, cookies=cookies)
    soup = BeautifulSoup(req.text, 'lxml')
    data = dict()
    try:
        data['title'] = soup.title.string
        if soup.find_all('input', attrs={'name': 'mp'}):
            data['page'] = int(soup.find('input', attrs={'name': 'mp'}).get('value'))
        else:
            data['page'] = 1
    except AttributeError:
        data['title'] = ''
        data['page'] = 0
    return data


def search_cn(keyword, cookies):
    # cookies = snatch_prepare()
    req = requests.Session().get('http://weibo.cn/', cookies=cookies)
    failure = 0
    while len(re.findall('登录|注册', req.text, re.S)) and failure < 5:
        failure += 1
        cookies = snatch_prepare()
        req = requests.Session().get('http://weibo.cn/', cookies=cookies)
    if failure == 5:
        logging.error('Getting cookies failed!')

    session = requests.Session()
    url = '''http://weibo.cn/search/mblog?hideSearchFrame=&keyword={}&advancedfilter=1&starttime=20170301&endtime=20170320&sort=time&page='''.format(urllib.request.quote(keyword))
    data = get_page_num(''.join([url, '1']), cookies)
    page_num = data['page']
    content_list = []
    # if page_num > 5:
    #     page_num = 5
    for i in range(1, page_num + 1):
        req = session.get(url=''.join([url, '{}'.format(i)]), cookies=cookies)
        while req.status_code != 200:
            logging.error('Snatch failed! Exitting...')
            exit(1)
        soup = BeautifulSoup(req.text, 'lxml')
        items = soup.find_all('div', 'c', id=True)
        for item in items:
            divs = item.find_all('div')
            content = dict({'uid': '', 'wb_id': '', 'nick': '', 'pub_date': '', 'pub_daytime': '', 'topic': '',
                            'at': '', 'original': 0, 'quote': '', 'comment': 0, 'forward': 0, 'like': 0, 'wb_url': '',
                            'content': '', 'from': '', 'pic_num': 0, 'grab_time': ''})
            content['wb_id'] = item.get('id').replace('M_', '')

            # todo: some unexpected exception from here which move the element in items[4]
            uid_result = re.findall('comment/{}[?]uid=(.*?)&'.format(content['wb_id']), divs[-1].decode(), re.S)
            if uid_result:
                content['uid'] = uid_result[0]
            content['nick'] = item.select('a.nk')[0].get_text()
            time_result = re.findall('收藏\s(.*?)\s来自', divs[-1].get_text(), re.S)
            if time_result:
                wb_time0 = time_result[0]
                wb_time1 = parsedate.parse_date(wb_time0)
                content['pub_date'] = wb_time1[0:10].replace('-', '/')
                content['pub_daytime'] = wb_time1[11:16]
            content['grab_time'] = parsedate.now_date()
            topic_result = re.findall('#(.*?)#', item.get_text(), re.S)
            if topic_result:
                for topic in topic_result:
                    content['topic'] = ''.join([content['topic'], '#', topic, '#'])
            if re.findall('转发了\xa0', item.get_text(), re.S):
                content['original'] = 1
            else:
                content['original'] = 0
            quote_result = item.select('span.cmt > a')
            if quote_result:
                content['quote'] = quote_result[0].get_text()
            # if item.select('span.ct > a'):
            #     content['from'] = ''.join(re.findall('\xa0来自[^>]+>(.*?)</', item.extract().decode(), re.S))
            # else:
            #     content['from'] = ''.join(re.findall('\xa0来自(.*?)</', item.extract().decode(), re.S))
            content['from'] = ''.join(re.findall('来自(.*)', divs[-1].get_text(), re.S))
            content['from'] = Filter.filteremoji(content['from'])
            content['like'] = ''.join(re.findall('\s赞\[(.*?)\]\s', divs[-1].get_text(), re.S))
            content['forward'] = ''.join(re.findall('\s转发\[(.*?)\]\s', divs[-1].get_text(), re.S))
            content['comment'] = ''.join(re.findall('\s评论\[(.*?)\]\s', divs[-1].get_text(), re.S))
            if content['original'] == 1:
                at_result = divs[-1].get_text().replace('转发理由:', '').split("\xa0\xa0")
                content['at'] = ''.join(re.findall('(@[\u4e00-\u9fa5a-zA-Z0-9]+)', at_result[0], re.S))    #  match some chinese behind @
                if len(divs) == 3:
                    at = divs[0].find_all('a')[0].get_text()
                    wb = item.select('div span.ctt')[0].get_text()
                    s = (divs[2].get_text().replace('转发理由:', '').split("\xa0\xa0")[0]
                         + '//@' + at + ':' + wb)
                    content['content'] = Filter.filteremoji(s).replace('\"', '\\"')
                    if re.findall('查看图片', divs[2].get_text(), re.S):
                        content['pic_num'] = 1
                elif len(divs) == 2:
                    at = divs[0].find_all('a')[0].get_text()
                    wb = item.select('div span.ctt')[0].get_text()
                    s = (divs[1].get_text().split("\xa0\xa0")[0] + '//@' + at + ':' + wb)
                    content['content'] = Filter.filteremoji(s).replace('\"', '\\"')
            elif content['original'] == 0:
                content['content'] = Filter.filteremoji(item.select('span.ctt')[0].get_text()).replace('\"', '\\"')
                content['at'] = ''.join(re.findall('(@[\u4e00-\u9fa5a-zA-Z0-9]+)', content['content'], re.S))
                if len(divs) == 2:
                    if divs[1].select('a img'):
                        pic_result = re.findall('>组图共(.*?)张<', divs[1].extract().decode(), re.S)
                        if pic_result:
                            content['pic_num'] = pic_result[0]
                        else:
                            content['pic_num'] = 1
            content['wb_url'] = 'http://weibo.com/{}/{}'.format(content['uid'], content['wb_id'])
            content_list.append(content)
        time.sleep(10)
    p = persist.Persist()
    for search_result in content_list:
        p.save_search_cn(search_result)
    p.conn.close()


def snatch_by_url(url, cookies, url_source, event_name):
    req = requests.Session().get('http://weibo.cn/', cookies=cookies)
    failure = 0
    while len(re.findall('登录|注册', req.text, re.S)) and failure < 5:
        failure += 1
        # cookies = snatch_prepare()
        req = requests.Session().get('http://weibo.cn/', cookies=cookies)
    if failure == 5:
        logging.error('Getting cookies failed!')
    ids = re.findall('weibo.com/(.*?)/(.*?)[?]', url, re.S)[0]
    url = 'http://weibo.cn/comment/{}?uid={}'.format(ids[1], ids[0])
    req = requests.Session().get(url=url, cookies=cookies)
    while req.status_code != 200:
        logging.error('Snatch failed! Exitting...')
        exit(1)
    soup = BeautifulSoup(req.text, 'lxml')
    content = dict({'uid': '', 'wb_id': '', 'nick': '', 'pub_date': '', 'pub_daytime': '', 'topic': '',
                    'at': '', 'original': 0, 'quote': '', 'comment': 0, 'forward': 0, 'like': 0, 'wb_url': '',
                    'content': '', 'from': '', 'pic_num': 0, 'grab_time': '', 'url_source': '', 'event_name': ''})
    content['uid'] = ids[0]
    content['wb_id'] = ids[1]
    content['like'] = re.findall('\s赞\[(.*?)\]\s', soup.get_text(), re.S)[0]
    forward_result = re.findall('\s转发\[(.*?)\]\s', soup.get_text(), re.S)
    if forward_result:
        content['forward'] = forward_result[0]
    else:
        content['forward'] = 0
    comment_result = re.findall('\s评论\[(.*?)\]\s', soup.get_text(), re.S)
    if comment_result:
        content['comment'] = comment_result[0]
    else:
        content['comment'] = 0

    item = soup.select('#M_')[0]
    divs = item.find_all('div')
    item.select('span.ct')[0]
    item_result = item.select('span.ct')[0].get_text().replace('    ', '')
    content['pub_date'] = parsedate.parse_date(item_result)[0:10].replace('-', '/')
    content['pub_daytime'] = parsedate.parse_date(item_result)[11:16]
    content['grab_time'] = parsedate.now_date()
    topic_result = re.findall('#(.*?)#', item.get_text(), re.S)
    if topic_result:
        for topic in topic_result:
            content['topic'] = ''.join([content['topic'], '#', topic, '#'])
    if re.findall('转发了\s', item.get_text(), re.S):
        content['original'] = 1
    else:
        content['original'] = 0
    quote_result = item.select('span.cmt > a')
    if quote_result:
        content['quote'] = quote_result[0].get_text()
    if content['original'] == 1:
        content['nick'] = ''.join(re.findall('\s(.*?)\s\s转发了', item.get_text(), re.S))
        at_result = divs[-1].get_text().replace('转发理由:', '').split("\xa0\xa0")
        content['at'] = ''.join(re.findall('(@[\u4e00-\u9fa5a-zA-Z0-9]+)', at_result[0], re.S))  # match some chinese behind @
        if len(divs) == 3:
            at = divs[0].find_all('a')[0].get_text()
            wb = item.select('div span.ctt')[0].get_text()
            s = (divs[2].get_text().replace('转发理由:', '').split("\xa0\xa0")[0] + '//@' + at + ':' + wb)
            content['content'] = Filter.filteremoji(s).replace('\"', '\\"')
            if re.findall('查看图片', divs[2].get_text(), re.S):
                content['pic_num'] = 1
        elif len(divs) == 2:
            at = divs[0].find_all('a')[0].get_text()
            wb = item.select('div span.ctt')[0].get_text()
            s = (divs[1].get_text().split("\xa0\xa0")[0] + '//@' + at + ':' + wb)
            content['content'] = Filter.filteremoji(s).replace('\"', '\\"')
    elif content['original'] == 0:
        content['nick'] = ''.join(re.findall('\s(.*?)\s:', item.get_text(), re.S))
        content['content'] = Filter.filteremoji(item.select('span.ctt')[0].get_text().replace(':', '')).replace('\"', '\\"')
        content['at'] = ''.join(re.findall('(@[\u4e00-\u9fa5a-zA-Z0-9]+)', content['content'], re.S))
        if len(divs) == 2:
            if divs[1].select('a img'):
                pic_result = re.findall('>组图共(.*?)张<', divs[1].extract().decode(), re.S)
                if pic_result:
                    content['pic_num'] = pic_result[0]
                else:
                    content['pic_num'] = 1
    content['event_name'] = event_name
    content['url_source'] = url_source
    content['wb_url'] = 'http://weibo.com/{}/{}'.format(content['uid'], content['wb_id'])

    p = persist.Persist()
    p.save_content_by_url(content)


def snatch_cn_comment(wb_id, uid, cookies):
    comment_list = []
    # 验证用户名 判断cookies是否可用于登录
    while len(re.findall('v寒楚石v', requests.Session().get('http://weibo.cn/', cookies=cookies).text, re.S)) == 0:
        logging.error('Getting cookies failed!')
        exit()
    comment_url = 'http://weibo.cn/comment/{}?retcode=6102'.format(wb_id)
    req = requests.Session().get(comment_url, cookies=cookies)
    soup = BeautifulSoup(req.text, 'lxml')
    page_result = re.findall('\s1/(.*?)页', soup.get_text(), re.S)
    if page_result:
        page_num = int(page_result[0])
    else:
        page_num = 1
    if page_num > 5:
        page_num = 5
    for i in range(1, page_num + 1):
        target = 'http://weibo.cn/comment/{}?retcode=6102&page={}'.format(wb_id, i)
        target_req = requests.Session().get(target, cookies=cookies)
        target_soup = BeautifulSoup(target_req.text, 'lxml')
        items = target_soup.find_all('div', 'c', id=True)
        for item in items:
            if not item.select(' > span'):
                continue
            comment = dict({'wb_id': '', 'cid': '', 'cuid': '', 'nick': '', 'uid': '', 'pub_date': '',
                            'pub_daytime': '', 'at': '', 'like': 0, 'comment': 0, 'content': '', 'from': '',
                            'grab_time': ''})
            comment['wb_id'] = wb_id
            comment['uid'] = uid
            comment['cid'] = item.get('id').replace('C_', '')
            comment['cuid'] = ''.join(re.findall('/spam/.*?&amp;fuid=(.*?)&', item.decode(), re.S))
            nick_result = re.findall('(\[热门\][\u4e00-\u9fa5a-zA-Z0-9-_]+:|[\u4e00-\u9fa5a-zA-Z0-9-_]+[\s]+:)', item.get_text(), re.S)
            if nick_result:
                comment['nick'] = nick_result[0].replace(':', '').replace(' ', '').replace('[热门]', '')
            comment['grab_time'] = parsedate.now_date()
            from_result = item.select('span.ct')
            if from_result:
                from_result = from_result[0].get_text()
                comment['from'] = ''.join(re.findall('来自(.*)', from_result, re.S))
                comment['from'] = Filter.filteremoji(comment['from'])
                time_result = re.findall('(.*?)\s来自', from_result, re.S)
                if time_result:
                    comment['pub_date'] = parsedate.parse_date(time_result[0])[0:10].replace('-', '/')
                    comment['pub_daytime'] = parsedate.parse_date(time_result[0])[11:16]
            comment['content'] = ''.join(re.findall(':(.*?)\s举报', item.get_text(), re.S))
            comment['content'] = Filter.filteremoji(comment['content']).replace('\"', '\\"')
            comment['at'] = ''.join(re.findall('(@[\u4e00-\u9fa5a-zA-Z0-9-_]+)', item.get_text(), re.S))
            like_result = re.findall('赞\[(\d+)\]', item.get_text(), re.S)
            if like_result:
                comment['like'] = like_result[0]
            comment_list.append(comment)
    p = persist.Persist()
    for comment_result in comment_list:
        p.save_comment_cn(comment_result)
    p.conn.close()


def snatch_cn_comment_forward(wb_id, uid, cookies):
    forward_list = []
    # 验证用户名 判断cookies是否可用于登录
    while len(re.findall('v寒楚石v', requests.Session().get('http://weibo.cn/', cookies=cookies).text, re.S)) == 0:
        logging.error('Getting cookies failed!')
        exit()
    comment_url = 'http://weibo.cn/repost/{}?uid={}'.format(wb_id, uid)
    req = requests.Session().get(comment_url, cookies=cookies)
    soup = BeautifulSoup(req.text, 'lxml')
    page_result = re.findall('\s1/(.*?)页', soup.get_text(), re.S)
    if page_result:
        page_num = int(page_result[0])
    else:
        page_num = 1
    if page_num > 5:
        page_num = 5
    for i in range(1, page_num + 1):
        target = 'http://weibo.cn/repost/{}?uid={}&page={}'.format(wb_id, uid, i)
        target_req = requests.Session().get(target, cookies=cookies)
        target_soup = BeautifulSoup(target_req.text, 'lxml')
        items = target_soup.select('div.c')
        for item in items:
            if not item.select(' > span'):
                continue
            comment = dict({'wb_id': '', 'fid': '', 'fuid': 0, 'nick': '', 'uid': '', 'pub_date': '',
                            'pub_daytime': '', 'at': '', 'like': 0, 'comment': 0, 'content': '', 'from': '',
                            'grab_time': ''})
            comment['wb_id'] = wb_id
            comment['uid'] = uid
            comment['fid'] = ''.join(re.findall('/attitude/(.*?)/add[?]', item.decode(), re.S))       # 转发的微博id
            # comment['cuid'] = ''.join(re.findall('/spam/.*?&amp;fuid=(.*?)&', item.decode(), re.S))
            nick_result = re.findall('([\u4e00-\u9fa5a-zA-Z0-9-_]+):', item.get_text(), re.S)
            if nick_result:
                comment['nick'] = nick_result[0]
            comment['grab_time'] = parsedate.now_date()
            from_result = item.select('span.ct')
            if from_result:
                from_result = from_result[0].get_text()
                comment['from'] = ''.join(re.findall('来自(.*)', from_result, re.S))
                comment['from'] = Filter.filteremoji(comment['from'])
                time_result = re.findall('\s(.*?)\s来自', from_result, re.S)
                if time_result:
                    comment['pub_date'] = parsedate.parse_date(time_result[0])[0:10].replace('-', '/')
                    comment['pub_daytime'] = parsedate.parse_date(time_result[0])[11:16]
            comment['content'] = ''.join(re.findall(':(.*?)\s赞\[', item.get_text(), re.S))
            comment['content'] = Filter.filteremoji(comment['content']).replace('\"', '\\"')
            comment['at'] = ''.join(re.findall('(@[\u4e00-\u9fa5a-zA-Z0-9-_]+)', item.get_text(), re.S))
            like_result = re.findall('赞\[(\d+)\]', item.get_text(), re.S)
            if like_result:
                comment['like'] = like_result[0]
            forward_list.append(comment)
    p = persist.Persist()
    for comment_result in forward_list:
        p.save_comment_forward_cn(comment_result)
    p.conn.close()


if __name__ == '__main__':
    cookies = {'_T_WM': 'xxxxx', 'SSOLoginState': 'xxxxx', 'SUHB': 'xxxxx', 'SUBP': 'xxxxx', 'SUB': 'xxxxx', 'SCF': 'xxxxx', 'ALF': 'xxxxx'}
    p0 = persist.Persist()
    # result = p0.query_data_uid_wbid()
    result = p0.query_data_uid_wbid_search()
    for result_item in result:
        snatch_cn_comment(result_item[1], result_item[0], cookies)
        logging.info('Snatch comment: Wb_id - {} is Finished!'.format(result_item[1]))
        snatch_cn_comment_forward(result_item[1], result_item[0], cookies)
        logging.info('Snatch comment_forward: Wb_id - {} is Finished!'.format(result_item[1]))
        time.sleep(10)

