# -*- coding: utf-8 -*-

import weibo_auto_handle

if __name__ == '__main__':
    # TODO: query account info from db
    account = dict()

    result = weibo_auto_handle.comment_prepare()
    weibo_auto_handle.comment(account, result['comment'], result['url'])
