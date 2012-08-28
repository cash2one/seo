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
import getgoogleorder

#cookie = Cookie.SimpleCookie()
#sim = SimHttp.SimBrowser(cookie)

class GetBaiduRank():
    def __init__(self):
        self.base = Base.Base()
        cookie = Cookie.SimpleCookie()
        self.sim = SimHttp.SimBrowser(cookie)
        self.UserAgent="Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 2.0.50727; InfoPath.2)";
        self.url_ref = 'wwww.baidu.com'

    def GetBaiduPage(self, key, page_num=0):
        '''get baidu search page of num page_num'''
        attrs = {'ie':'utf-8', 'pn':'0'}
        attrs['pn'] = str(page_num * 10)
        url_attrs = urllib.urlencode(attrs)
        url_domain = 'http://www.baidu.com/s?'
        url = url_domain + url_attrs + '&wd='
        url += key.encode('utf-8')
        header = {'Referer':self.url_ref,'User-Agent':self.UserAgent}    
        res,Fhtml = self.sim.request(url,'GET',headers=header);

        try:
            content = Fhtml.decode('utf-8')
        except:
            content = ''
        self.url_ref = url
        return content
        #print url
        #return self.base.GetHtmlPage(url)''

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

    def GetBaiduPageNum(self, html_src):
        num = self.base.FindSection(html_src, '<span class="nums"', '</span>')
        #print num 
        if len(num) != 1:
            return ''
        ret = num[0].split(u'约')[1].split(u'个')
        #print ret[0]
        return ret[0]

    def GetBaiduNum(self, key):
        html_src = self.GetBaiduPage(key)
        return self.GetBaiduPageNum(html_src)

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

    def GetBaiduPageFull(self, key, target_url, pagenum=5):
        search_key = key
        baidu_num = 0
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

    def GetHost(self, url):
        if url.find('www.') != -1:
            return url.replace('www.', '.')
        return url

    def get_rank_of_group(self, group, sqlconn):
        keywords = group[2].split('#')
        for key in keywords:
            ret = [str(group[0]), key]
            my_url = self.GetHost(group[3])
            cmp_url = self.GetHost(group[4])
            print key, my_url, cmp_url
            if group[5] == 1:
                my_rank, my_rank_url = self.GetBaiduPageFull(key, my_url)
                other_rank, other_rank_url = self.GetBaiduPageFull(key, cmp_url)
                #my_rank, other_rank, my_rank_url, other_rank_url = self.GetBaiduPageFull(key, group[3], group[4])
                # 添加baidu排名情况
                ret.append(my_rank + '|' + other_rank)
                ret.append(my_rank_url + '|' + other_rank_url)
                #ret.append('')
                google_ranker = getgoogleorder.TGoogleOrder(key.encode('utf-8'), my_url, cmp_url)
                r_1, r_2 = google_ranker.getFixRank()
                #r_1 = 0
                #r_2 = 0
                # 添加google排序情况 google没有url
                ret.append(str(r_1) + '|' + str(r_2))
                ret.append('|')
            elif group[5] == 2:
                # 添加百度竞价排名
                my_rank, my_rank_url = self.GetBaiduFixRank(key, my_url)
                other_rank, other_rank_url = self.GetBaiduFixRank(key, cmp_url)
                ret.append(my_rank + '|' + other_rank)
                ret.append(my_rank_url + '|' + other_rank_url)
                # google竞价排名为空
                ret.append('|')
                ret.append('|')
            ret.append('unknown flow')
            #ret.append(self.GetBaiduNum(key))
            #ret.append(Get
            #print ret
            #sqlconn.insert_multi(ret, 'rank_compare')
            print 'sleep for next keyword...'
            #time.sleep(2)
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
            #time.sleep(5)
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
