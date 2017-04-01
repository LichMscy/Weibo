# -*-coding: utf-8-*-

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

    def query_task(self):
        sql = '''select task_id, url, num, keywords from t_task_ic where status = 0 and `type` = 2/*and start_time <= now() and end_time >= now()*/
ORDER BY task_id DESC limit 1'''
        try:
            self.cur.execute(sql)
            result = self.cur.fetchall()
        except:
            raise
        self.conn.close()
        return result

    def query_comment(self, clib_id):
        sql = '''select content from t_comment_lib where clib_id = %s''' % clib_id
        try:
            self.cur.execute(sql)
            result = self.cur.fetchall()
        except:
            raise
        self.conn.close()
        return result

    def insert_news(self, news):
        sql = '''
insert into t_news(platform_id, media_name, title, summary, src_url, task_id, comment_num, like_num, forward_num,
create_time) values("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")''' \
        % (news['platform_id'], news['media_name'], news['title'], news['summary'], news['src_url'], news['task_id'],
           news['comment_num'], news['like_num'], news['forward_num'], news['create_time'])
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise
        self.conn.close()

    def update_task_status(self, task_id):
        sql = '''update t_task_ic set status = 2 where task_id = "%s"''' % task_id
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise
        self.conn.close()

    def query_account(self):
        sql = '''
select id, account_id, password, cookies from t_account_lib where status = 0 and platform_id = 2 limit 1'''
        try:
            self.cur.execute(sql)
            result = self.cur.fetchall()
        except:
            raise
        self.conn.close()
        return result

    def save_account_cookies(self, account_id, cookies, update_time):
        sql = '''
update t_account_lib set cookies = "%s", update_time = "%s" where id = "%s"''' % (cookies, update_time, account_id)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise
        self.conn.close()
