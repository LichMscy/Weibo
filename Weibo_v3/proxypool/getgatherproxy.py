# -*- coding: utf-8 -*-

import re
import ast
import json
import datetime
import requests
import MySQLdb

MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_DB = 'xxxxx'
MYSQL_USER = 'xxxxx'
MYSQL_PASSWD = 'xxxxx'

headers = {
    'Host': 'www.gatherproxy.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,und;q=0.4',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/55.0.2883.87 Safari/537.36',
    'Referer': 'http://www.gatherproxy.com/proxylist/country/?c=China',
}
list0 = []

page_num = 0
insert_sql = '''
insert into wb_proxy_pool (`proxy_ip`, `proxy_port`, `proxy_addr`, `anonymity_level`, `uptime_l`, `uptime_d`, `response`,
`status`, `update_time`, `grab_time`, `remark`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
update_sql = '''
update wb_proxy_pool set `proxy_ip` = %s, `proxy_port` = %s, `proxy_addr` = %s, `anonymity_level` = %s, `uptime_l` = %s,
`uptime_d` = %s, `response` = %s, `status` = %s, `update_time` = %s, `grab_time` = %s, `remark` = %s
where `proxy_ip` = %s and `proxy_port` = %s'''
update_access_sql = '''
update wb_proxy_pool set `baidu_access` = %s, `weibo_access` = %s, `weixin_access` = %s
where `proxy_ip` = %s and `proxy_port` = %s'''


def post_request(u, header):
    html = requests.get(u, headers=header, timeout=10).text
    return html


def parse_html(html, proxy_list):
    reg0 = '(?<=insertPrx\().*\}'
    list1 = re.findall(reg0, html)
    localtime = datetime.datetime.now()
    for list2 in list1:
        l = ast.literal_eval(list2.replace('null', '\"null\"'))
        ip = l['PROXY_IP']
        port = int(l['PROXY_PORT'], 16)
        addr = l['PROXY_COUNTRY'] + l['PROXY_CITY']
        level = l['PROXY_TYPE']
        live = l['PROXY_UPTIMELD'].split('/')[0]
        dead = l['PROXY_UPTIMELD'].split('/')[1]
        response = l['PROXY_TIME'] + 'ms'
        status = l['PROXY_STATUS']
        raw = l['PROXY_LAST_UPDATE'].split(' ')
        update = (localtime - datetime.timedelta(minutes=int(raw[0]), seconds=int(raw[1]))).strftime("%Y-%m-%d %H:%M:%S")
        grab = localtime.strftime("%Y-%m-%d %H:%M:%S")
        remark = 'insert'
        list1 = [ip, port, addr, level, live, dead, response, status, update, grab, remark]
        proxy_list.append(list1)
    return proxy_list


def query_pool(cursor):
    try:
        sql = 'select proxy_ip, proxy_port from wb_proxy_pool'
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
    except Exception as e0:
        print(e0)


def insert_db(sql, list1, connection, cursor):
    try:
        cursor.execute(sql, list1)
        connection.commit()
    except Exception as e1:
        connection.rollback()
        print(e1)


def update_db(sql, list1, connection, cursor):
    try:
        cursor.execute(sql, list1)
        connection.commit()
    except Exception as e2:
        connection.rollback()
        print(e2)


def update_access(sql, list1, connection, cursor):
    try:
        cursor.execute(sql, list1)
        connection.commit()
    except Exception as e2:
        connection.rollback()
        print(e2)

if __name__ == '__main__':
    a = b = 0
    try:
        # proxies = {
        #     'http': 'http://'+ip+':'+port,
        #     'https': 'http://'+ip+':'+port,
        # }
        # for i in range(1, page_num + 1):
        url = 'http://www.gatherproxy.com/proxylist/country/?c=China'
        req = post_request(url, headers)
        list0 = parse_html(req, list0)
    except Exception as e:
        print(Exception, e)

    try:
        conn = MySQLdb.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            passwd=MYSQL_PASSWD,
            database=MYSQL_DB,
            charset='utf8',
        )
        cur = conn.cursor()
        items = query_pool(cur)
        for j in list0:
            list3 = list()
            list3.append(j[0])
            list3.append(j[1])
            if tuple(list3) not in items:
                a += 1
                insert_db(insert_sql, j, conn, cur)
            else:
                j.append(j[0])
                j.append(j[1])
                j[10] = 'update'
                b += 1
                update_db(update_sql, j, conn, cur)

        print('update data:%d times, insert:%d times.' % (b, a))
        conn.close()
    except Exception as e:
        print(Exception, e)
