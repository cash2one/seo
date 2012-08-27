# -*-coding:utf-8 -*-

#
# base functions and class for all
#

import SimHttp
import Cookie
import time

class Base():
    def __init__(self):
        self.sim = init_sim()

    def init_sim(self):
        cookie = Cookie.SimpleCookie()
        return SimHttp.SimBrowser(Cookie)

    def FindSection(self, html_src, start_tag, end_tag):
        '''return the content between the start_tag and end_tag'''
        idx = 0
        ret = []
        while True:
            s_tab = html_src.find(start_tag, idx)
            if (s_tab == -1):
                break
            e_tab = html_src.find(end_tag, s_tab)
            #e_tab += len(end_tag)
            s_tab += len(start_tag) + 1
            #print html_src[s_tab:e_tab]
            ret.append(html_src[s_tab:e_tab])
            idx = e_tab
        return ret

    def GetHtmlPage(self, url):
        re, content = sim.request(url, 'GET')
        try:
            dec_src = content.decode('utf-8')
        except:
            print 'decode html_src of', url, 'error, continue...'
            print html_src
            return ''
        return html_src
