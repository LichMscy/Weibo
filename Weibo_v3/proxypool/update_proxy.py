# -*-coding: utf-8-*-

import datetime
import MySQLdb
import requests


def updateproxypool():
    results = []
    conn = MySQLdb.connect(
        host="xxxxx",
        port=3306,
        user="xxxxx",
        passwd="xxxxx",
        database="xxxxx",
        charset='utf8',
    )
    cur = conn.cursor()
    select_sql = 'select proxy_ip, proxy_port from wb_proxy_pool'
    update_sql = '''
    update wb_proxy_pool set `update_time` = %s, `baidu_access` = %s, `weibo_access` = %s, `weixin_access` = %s
    where `proxy_ip` = %s and `proxy_port` = %s'''
    delete_sql = '''
    delete from wb_proxy_pool where `proxy_ip` = %s and `proxy_port` = %s'''
    try:
        cur.execute(select_sql)
        results = cur.fetchall()
    except Exception as e0:
        print(e0)
    for item in results:
        link = 'http://' + item[0] + ':' + str(item[1])
        accesslist = []
        update = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        accesslist.append(update)
        try:
            accesslist.append(requests.get('https://www.baidu.com', proxies={'http': link}, timeout=3).status_code)
        except:
            accesslist.append('')
        try:
            accesslist.append(requests.get('http://weibo.cn', proxies={'http': link}, timeout=3).status_code)
        except:
            accesslist.append('')
        try:
            accesslist.append(requests.get('https://mp.weixin.qq.com', proxies={'http': link}, timeout=3).status_code)
        except:
            accesslist.append('')

        accesslist.extend(item)
        if accesslist[2] == 200:
            try:
                cur.execute(update_sql, accesslist)
                conn.commit()
            except Exception as e1:
                conn.rollback()
                print(e1)
            # print('updated %s:%s' % (item[0], item[1]))
        else:
            try:
                cur.execute(delete_sql, item)
                conn.commit()
            except Exception as e2:
                conn.rollback()
                print(e2)
            print('delete %s:%s' % (item[0], item[1]))
    print('Update access complete!')
    conn.close()

if __name__ == '__main__':
    updateproxypool()
