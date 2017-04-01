# -*- coding: utf-8 -*-

import weibo_auto_handle

if __name__ == '__main__':
    cookies = weibo_auto_handle.update_cookies()
    weibo_auto_handle.snatch_news_info(cookies)
