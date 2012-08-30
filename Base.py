# -*-coding:utf-8 -*-

#
# base functions and class for all
#

import SimHttp
import Cookie
import time

class Base():
    def __init__(self):
        self.sim = self.init_sim()

    def init_sim(self):
        cookie = Cookie.SimpleCookie()
        return SimHttp.SimBrowser(cookie)

    def FindSection(self, html_src, start_tag, end_tag):
        '''return the content between the start_tag and end_tag'''
        idx = 0
        ret = []
        while True:
            s_tab = html_src.find(start_tag, idx)
            if (s_tab == -1):
                break
            s_tab += len(start_tag)
            e_tab = html_src.find(end_tag, s_tab)
            ret.append(html_src[s_tab:e_tab])
            idx = e_tab
        return ret

    def GetHtmlPage(self, url):
        re, content = self.sim.request(url, 'GET')
        if 'status' not in re or re['status'] != '200':
            # 如果打开url失败，重置http连接
            self.sim = SimHttp.SimBrowser(Cookie.SimpleCookie())
        # 尝试解码网页内容
        try:
            dec_src = content.decode('utf-8')
        except:
            try:
                dec_src = content.decode('gbk')
            except:  
                return ''
        return dec_src
