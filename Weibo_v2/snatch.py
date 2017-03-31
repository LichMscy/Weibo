# -*- coding: utf-8 -*-


import re
import weibo
import searchuid
from time import sleep


def main(a, b):
    array = []
    proxy = ['116.255.192.209:808', '183.246.160.78	:8998', '120.92.3.127:80', '120.52.73.97:80', '120.52.73.98:100',
             '125.88.74.122:83', '60.205.206.57:138', '60.205.205.90:139', '60.205.183.123:139', '60.205.207.235:139',
             '60.205.220.176:139', '60.205.207.233:138']
    s = searchuid.GetUid()
    l = s.execute_sql(a, b)
    w = weibo.Weibo()
    for i in l:
        print('Snatching %s' % i['username'])
        uid = i['url'].split('/')[-1]
        if len(re.findall('\D', uid)) != 0 or uid == '':
            uids = w.get_uid(i['username'])
            if uids == '':
                array.extend(i['username'])
                print('wb info is wrong!')
                continue
            else:
                uid = uids[0]
        url = 'http://weibo.cn/%s' % uid
        data = w.get_info(url)
        if data['page'] == 0:
            print('Cookie is out of date!')
            continue
        contents = w.fetch_content(uid, data['page'], proxy)
        print(len(contents))
        s1 = searchuid.GetUid()
        for j in contents:
            s1.save_content(j)
            # if status == 0:
            # elif status == 1:
        s1.cur.close()
        s1.conn.close()
        print('%s snatch success!' % i['username'])
        # sleep(5)
    print('snatch complete!')


if __name__ == '__main__':
    main(242, 17712)  # 全球时尚先锋榜
