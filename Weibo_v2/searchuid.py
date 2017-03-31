# -*- coding: utf-8 -*-


import MySQLdb


class GetUid:
    def __init__(self):
        self.conn = MySQLdb.connect(
            host="xxxxx",
            port=3306,
            user="xxxxx",
            passwd="xxxxx",
            database="xxxxx",
            charset='utf8',
        )
        self.cur = self.conn.cursor()
        self.dic = dict()
        self.lis = []

    def execute_sql(self, s, e):
        sql = 'select wb_url, wb_name from t_media_wb where id ' \
              'between %d and %d' % (s, e)
        try:
            self.cur.execute(sql)
            data = self.cur.fetchall()
            for row in data:
                self.dic['url'] = row[0]
                self.dic['username'] = row[1]
                self.lis.append(dict(self.dic))
            return self.lis
        except:
            print('Error: unable to fetch data from db')
        self.conn.close()

    def save_content(self, content):
        sql = 'insert into wb_content(wb_id, content_id, content_url, content, pic, forward, comment, `like`, `type`, `from`, pub_time, grab_time) ' \
              'values("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' \
              % (content['uid'], content['id'], content['url'], content['content'], content['pic'], content['forward'],
                 content['comment'], content['like'], content['type'], content['from'], content['pub_time'], content['grab_time'])

        try:
            self.cur.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            print(sql)
            print('fail to insert %s' % content['url'])
