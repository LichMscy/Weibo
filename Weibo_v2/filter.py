# -*- coding: utf-8 -*-


import re


class Filter:
    '''
    过滤微博内容中的emoji表情
    '''
    def filteremoji(self):
        try:
            co = re.compile(u'[\U00010000-\U0010ffff]')
        except re.error:
            co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        return co.sub('', self)
