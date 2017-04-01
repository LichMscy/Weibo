# -*-coding: utf-8-*-

import MySQLdb


class Persist:
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

    def selectproxy(self):
        proxylist = list(dict())
        sql = 'select proxy_ip, proxy_port from wb_proxy_pool where weibo_access = 200 ORDER BY RAND()'
        self.cur.execute(sql)
        results = self.cur.fetchall()
        for items in results:
            proxystr = 'http://' + items[0] + ':' + str(items[1])
            proxylist.append({'http': proxystr})
        self.conn.close()
        return proxylist

    def select_raw_task_info(self, s):
        info = list()
        sql = '''select id, wb_name, wb_url from wb_task_unofficial where status = 0 and SUBSTRING_INDEX(wb_url, '/', -1) = '' limit %d, 100''' % s
        try:
            self.cur.execute(sql)
            info = self.cur.fetchall()
        except Exception as e:
            print(e)
        self.conn.close()
        return info

    def select_raw_info(self, s):
        info_list = list()
        sql = '''select id, wb_id from wb_task_unofficial where !ISNULL(wb_id) and status = 1 limit %d, 1''' % s
        try:
            self.cur.execute(sql)
            data = self.cur.fetchall()
            for row in data:
                dic = dict()
                dic['id'] = row[0]
                dic['wb_id'] = row[1]
                info_list.append(dic)
        except Exception as e:
            print(e)
        self.conn.close()
        return info_list

    def save_patch_task_status(self, task_id):
        sql = '''update wb_task_unofficial set status = 3 where id = %d''' % task_id
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise
        self.conn.close()

    def save_content(self, content):
        sql = '''
            insert into wb_content(wb_id, content_id, content_url, content, pic, forward, `comment`, `like_num`, `type`,
            `from`, pub_time, grab_time) values("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")''' \
              % (content['uid'], content['id'], content['url'], content['content'], content['pic'], content['forward'],
                 content['comment'], content['like'], content['type'], content['from'], content['pub_time'],
                 content['grab_time'])
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(sql)
            print(e)

    #
    def update_wbinfo(self, wb_id, uid):
        sql = '''
        update t_media_wb_order set wb_id = "%s" where id = "%s"''' \
              % (wb_id, uid)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(e)
        self.conn.close()

    # select wb_id list from table `wb_media`
    def select_wb_media_list(self):
        info_list = list()
        sql = '''
          select wb_id from wb_media'''
        try:
            self.cur.execute(sql)
            info_list = self.cur.fetchall()
        except Exception as e:
            print(e)
        self.conn.close()
        return info_list

    # save basic info to table `wb_media`
    def save_wb_media_info(self, info):
        sql = '''
                insert into wb_media(wb_id, wb_url, wb_name, sex, verify, focus, fans, wb_nums, intro, avatar, province,
                verified, create_time) values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')''' \
              % (
              info['wb_id'], info['wb_url'], info['wb_name'], info['sex'], info['verify'], info['focus'], info['fans'],
              info['wb_nums'], info['intro'], info['avatar'], info['province'], info['verified'], info['create_time'])
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise

    # update wb_id into table `wb_task` for wb_id in task is exists
    def update_id_into_wb_task(self, wb_id, task_id):
        sql = '''
            update wb_task set wb_id = '%s' where id= '%s' ''' % (wb_id, task_id)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise
        self.conn.close()

    # get new task from table `wb_task`
    def get_new_task(self):
        sql = '''
select wb_url, wb_name, id from wb_task where start_time <= now() and end_time >= now()
and (status = 0 or status = 1)'''
        try:
            self.cur.execute(sql)
            result = self.cur.fetchall()
        except:
            raise  # TODO: define customize Mysql Exception
        self.conn.close()
        return result

    # update status of task in table `wb_task`
    def update_task_status(self, status, url, name):
        sql = '''
update wb_task set status = %d where wb_url = "%s" and wb_name = "%s"''' % (status, url, name)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise
        self.conn.close()

    # update status of task in table `wb_task_unofficial`
    def update_batch_task_status(self, task_id, wb_id, status, wb_former):
        sql = '''
update wb_task_unofficial set wb_id = "%s", status = %d, wb_former = %d where id = %d ''' \
              % (wb_id, status, wb_former, task_id)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            raise
        self.conn.close()
