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
            #e_tab += len(end_tag)
            #print html_src[s_tab:e_tab]
            ret.append(html_src[s_tab:e_tab])
            idx = e_tab
        return ret

    def GetHtmlPage(self, url):
        re, content = self.sim.request(url, 'GET')
        #print re
        if 'status' not in re or re['status'] != '200':
            #return ''
            self.sim = SimHttp.SimBrowser(Cookie.SimpleCookie())
        try:
            dec_src = content.decode('utf-8')
        except:
            print 'decode html_src of', url, 'error, continue...'
            #print dec_src
            return ''
        return dec_src
