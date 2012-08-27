# -*-coding:utf-8 -*-
#! /bin/bash

# BaiduRank.py

import urllib
import HTMLParser
import re
import sqliteconn
import SimHttp
import Cookie
import time
import Base

#cookie = Cookie.SimpleCookie()
#sim = SimHttp.SimBrowser(cookie)

class GetBaiduRank():
    def __init__(self):
        self.base = Base.Base()

    def GetBaiduPage(self, key, page_num=0):
        '''get baidu search page of num page_num'''
        attrs = {'ie':'utf-8', 'pn':'0'}
        attrs['pn'] = str(page_num * 10)
        url_attrs = urllib.urlencode(attrs)
        url_domain = 'http://www.baidu.com/s?'
        url = url_domain + url_attrs + '&wd='
        url += key.encode('utf-8')
        #print url
        return self.base.GetHtmlPage(url)

    def AnaylsisBdSearchHtml(self, html):
        table_ret = self.base.FindSection(html, '<table', '>')
        #print table_ret
        ret = []
        for table in table_ret:
            #print table
            rank_id = self.base.FindSection(table, 'id="', '"')
            #print rank_id
            if len(rank_id) != 1:
                continue
            if int(rank_id[0]) > 100:
                continue
            rank_url = self.base.FindSection(table, 'mu="', '"')
            if len(rank_url) != 1:
                continue
            ret.append([rank_id[0], rank_url[0]])
        return ret
       #pass

    def GetFixLink(self, html_src):
        '''get all fix link in the page'''
        idx = 0
        ret = []
        table_section = self.base.FindSection(html_src, '<table', '</table>')
        if len(table_section) == 0:
            return ['error link']
        right_rank = self.base.FindSection(table_section[0], '<font size="-1" color="#008000">', '</font>')
        left_rank = []
        for item in table_section[1:]:
            font = self.base.FindSection(item, '<font size=-1 color="#008000">', '</font>')
            left_rank.extend(font)
        left_rank.extend(right_rank)
        #for i in left_rank:
        #    print i
        return left_rank

    def find_table(self, html_src, start):
        s = html_src.find('<table', start)
        if s == -1:
            return -1, ''
        e = html_src.find('>', s)
        return e+1, html_src[s:e+1]
    
    def GetBaiduNatureRank(self, html_src, target_url):
        links = self.AnaylsisBdSearchHtml(html_src)
        #ret_1 = 0
        #ret_2 = 0
        #ret_url_1 = ''
        #ret_url_2 = ''
        for link in links:
            #print link
            if link[1].find('http://www.baidu.com/link?url') != -1:
                content = self.base.GetHtmlPage(link[1])
                url = self.base.FindSection(content, 'href="', '"')
                if len(url) == 0:
                    continue
                #print url
                #print content
                link[1] = url[0]
            if link[1].find(target_url) != -1:
                return link[0], link[1]
        return 0, ''

#                ret_1 = link[0]
#                ret_url_1 = link[1]
#            elif link[1].find(cmp_url) != -1:
#                ret_2 = link[0]
#                ret_url_2 = link[1]
#
#        return ret_1, ret_2, ret_url_1, ret_url_2

        idx = 0
        htmlparser = FindUrlParser(target_url)
        while True:
            idx, content = self.find_table(html_src, idx)
            if idx == -1:
                break
            htmlparser.feed(content)
            if htmlparser.rank != 0:
                return htmlparser.rank, htmlparser.rank_url
        return 0, ''

    def GetBaiduPageFull(self, key, target_url, pagenum=5):
        search_key = key
        for i in xrange(0, pagenum):
            html = self.GetBaiduPage(search_key, i)
            if html == '':
                return '-1',''
                #continue
            rank, rank_url = self.GetBaiduNatureRank(html, target_url)
            if rank != 0:
                return str(rank), rank_url
                #return rank
        return '0',''

    def GetBaiduFixRank(self, key, target_url):
        search_key = key
        html = self.GetBaiduPage(search_key)
        # if couldn't open the url, return -1
        if html == '':
            return '-1',''
        
        link = self.GetFixLink(html)
        for i in xrange(0, len(link)):
            if link[i].find(target_url) != -1:
                return str(i + 1), link[i].split(' ')[0]
        return '0',''

    def get_rank_of_group(self, group, sqlconn):
        keywords = group[2].split('#')
        for key in keywords:
            ret = [str(group[0]), key]
            if group[5] == 1:
                my_rank, my_rank_url = self.GetBaiduPageFull(key, group[3])
                other_rank, other_rank_url = self.GetBaiduPageFull(key, group[4])
                #my_rank, other_rank, my_rank_url, other_rank_url = self.GetBaiduPageFull(key, group[3], group[4])
                ret.append(my_rank + '|' + other_rank)
                ret.append(my_rank_url + '|' + other_rank_url)
                ret.append('')
                ret.append('')
            elif group[5] == 2:
                ret.append('')
                ret.append('')
                my_rank, my_rank_url = self.GetBaiduFixRank(key, group[3])
                other_rank, other_rank_url = self.GetBaiduFixRank(key, group[4])
                ret.append(my_rank + '|' + other_rank)
                ret.append(my_rank_url + '|' + other_rank_url)
            ret.append('unknown flow')
            #print ret
            #sqlconn.insert_multi(ret, 'rank_compare')
            print 'sleep for next keyword...'
            time.sleep(2)
            yield ret

    def thread_rank(self, sqlconn_name):
        sqlconn = sqliteconn.sqlconn(sqlconn_name)
        group_ret = sqlconn.read_group_info('group_info_rank')
        for group in group_ret:
            for key_rank_ret in self.get_rank_of_group(group, sqlconn):
                print key_rank_ret
                sqlconn.insert_multi(key_rank_ret, 'rank_compare')
            #after read a group, sleep for 10 seconds
            print 'after read a group, sleep for a while...'
            #time.sleep(10)

    def mock_thread_rank(self, sqlconn_name):
        sqlconn = sqliteconn.sqlconn(sqlconn_name)
        group_ret = sqlconn.read_group_info('group_info_rank')
        for group in group_ret:
            for key_rank_ret in self.get_rank_of_group(group, sqlconn):
                print key_rank_ret
            #after read a group, sleep for 10 seconds
            print 'sleep for next group...'
            time.sleep(5)
            #break

class FindUrlParser(HTMLParser.HTMLParser):
    ''' '''
    def __init__(self, url):
        HTMLParser.HTMLParser.__init__(self)
        self.rank = 0
        self.rank_url = ''
        self.url = url

    def handle_starttag(self, tag, attrs):
        ret_tmp = 0
        if 'table' == tag:
            for key, value in attrs:
                if key == 'id':
                    try:
                        self.ret_tmp = int(value)
                        if self.ret_tmp > 100:
                            self.ret_tmp = 0
                    except:
                        self.ret_tmp = 0
                if key == 'mu':
                    print '---', value, self.url
                    if value.find(self.url) != -1:
                        self.rank = self.ret_tmp
                        self.rank_url = value

def thread_rank(sqlconn_name):
    rank_getter = GetBaiduRank()
    rank_getter.thread_rank(sqlconn_name)

if __name__ == '__main__': 
    rank_getter = GetBaiduRank()
    while True:
        rank_getter.mock_thread_rank('company.db')
    #thread_rank('company.db')
    #print GetBaiduPageFull('鲜花', 'bj.58.com')
    #print GetBaiduFixRank('鲜花', 'zhenaihuawu.com')
    #thread_rank()
    #thread_query()
    #GetBaiduNum(u'鲜花')
