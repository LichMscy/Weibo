# -*- coding: utf-8 -*-


import datetime
import re


def parse_date(self):
    localtime = datetime.datetime.now()
    if re.compile('\d+分钟前').findall(self):
        return (localtime - datetime.timedelta(minutes=int(self[:-3]))).strftime("%Y-%m-%d %H:%M")
    elif re.compile('今天').findall(self):
        return localtime.strftime("%Y-%m-%d %H:%M")[0:11] + str(datetime.timedelta(hours=int(self[3:5]), minutes=int(self[6:8])))
    elif re.compile('\d+月\d+日').findall(self):
        return localtime.strftime("%Y-%m-%d %H:%M")[0:5] + self[0:2] + '-' + self[3:5] + ' ' + self[7:9] + ':' + self[10:12] + ':00'
    elif re.compile('\d{4}-\d{2}-\d{2}').findall(self):
        return self
    return


def now_date():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return now
