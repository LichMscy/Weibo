# -*- coding: utf-8 -*-

import MySQLdb


class Persist:
    def __init__(self):
        self.conn = MySQLdb.connect(
            host="localhost",
            port=3306,
            user="xxxxx",
            passwd="xxxxx",
            database="xxxxx",
            charset='utf8',
        )
        self.cur = self.conn.cursor()

    def save_search_cn(self, content):
        sql = '''
insert into wb_data_search(uid, wb_id, wb_url, nick, content, topic, `at`, original, quote, `comment`, forward, `like`, 
pic_num, `from`, pub_date, pub_daytime, grab_time) values("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s",
"%s", "%s", "%s", "%s", "%s", "%s", "%s")''' \
              % (content['uid'], content['wb_id'], content['wb_url'], content['nick'], content['content'],
                 content['topic'], content['at'], content['original'], content['quote'], content['comment'],
                 content['forward'], content['like'], content['pic_num'], content['from'], content['pub_date'],
                 content['pub_daytime'], content['grab_time'])
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise

    def save_content_by_url(self, content):
        sql = '''
        insert into wb_data_url(uid, wb_id, wb_url, nick, content, topic, `at`, original, quote, `comment`, forward, 
        `like`, pic_num, `from`, pub_date, pub_daytime, grab_time, url_source, event_name) values("%s", "%s", 
        "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")''' \
              % (content['uid'], content['wb_id'], content['wb_url'], content['nick'], content['content'],
                 content['topic'], content['at'], content['original'], content['quote'], content['comment'],
                 content['forward'], content['like'], content['pic_num'], content['from'], content['pub_date'],
                 content['pub_daytime'], content['grab_time'], content['url_source'], content['event_name'])
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise
        self.conn.close()

    def save_comment_cn(self, comment):
        sql = '''insert into wb_data_comment(wb_id, comment_id, comment_uid, nick, uid, pub_date, pub_daytime, at, 
`like`, `comment`, content, `from`, grab_time) values("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", 
"%s", "%s", "%s")''' \
              % (comment['wb_id'], comment['cid'], comment['cuid'], comment['nick'], comment['uid'], comment['pub_date'],
                 comment['pub_daytime'], comment['at'], comment['like'], comment['comment'],
                 comment['content'], comment['from'], comment['grab_time'])
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(''.join([e, 'SQL is:', sql]))
            # raise

    def save_comment_forward_cn(self, comment):
        sql = '''insert into wb_data_comment_forward(wb_id, forward_id, forward_uid, nick, uid, pub_date, pub_daytime, at, 
        `like`, `comment`, content, `from`, grab_time) values("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", 
        "%s", "%s", "%s")''' \
              % (comment['wb_id'], comment['fid'], comment['fuid'], comment['nick'], comment['uid'],
                 comment['pub_date'], comment['pub_daytime'], comment['at'], comment['like'], comment['comment'],
                 comment['content'], comment['from'], comment['grab_time'])
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(''.join([e, 'SQL is:', sql]))
            # raise

    def query_data_uid_wbid(self):
        sql = '''select a.uid, a.wb_id from wb_data_url a LEFT JOIN wb_data_comment b ON a.wb_id = b.wb_id WHERE b.wb_id IS NULL'''
        try:
            self.cur.execute(sql)
            result = self.cur.fetchall()
        except:
            raise
        self.conn.close()
        return result

    def query_data_uid_wbid_search(self):
        sql = '''select a.uid, a.wb_id from wb_data_search a LEFT JOIN wb_data_comment b ON a.wb_id = b.wb_id WHERE b.wb_id IS NULL'''
        try:
            self.cur.execute(sql)
            result = self.cur.fetchall()
        except:
            raise
        self.conn.close()
        return result
