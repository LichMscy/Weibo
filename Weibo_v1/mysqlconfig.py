# -*-coding:utf8-*-

import MySQLdb as mysqldb

url = []
name = []


conn = mysqldb.connect(
    host="xxxxx",
    port=3306,
    user="xxxxx",
    passwd="xxxxx",
    database="xxxxx",
    charset='utf8',
)
cur = conn.cursor()
sql = "select wb_url,wb_name from t_media_wb limit 100"

try:
    cur.execute(sql)
    data = cur.fetchall()
    for row in data:
        url.append(row[0])
        name.append(row[1])
except:
    print("Error: unable to fetch data from db.")

cur.close()
conn.close()


def link(self):
    return url


def username(self):
    return name
