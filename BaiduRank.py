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
import random

#cookie = Cookie.SimpleCookie()
#sim = SimHttp.SimBrowser(cookie)

class GetBaiduRank():
    def __init__(self):
        self.base = Base.Base()

    def GetPage(self, url):
        header = {'Referer':self.url_ref,'User-Agent':self.UserAgent}    
        res,Fhtml = self.sim.request(url,'GET',headers=header);
        #print res
        if 'status' not in res or res['status'] != '200':
            print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n>>>>>>>>>>>>>>>>>>>>>>>>>>>'
            #print Fhtml.decode('gbk')
            return ''
        try:
            content = Fhtml.decode('utf-8')
        except:
            content = ''
        self.url_ref = url
        return content

    def GetBaiduSearchPages(self, key, flag_reload=True):
        # 每次抓取一个key， 复原http的信息
        self.sim = SimHttp.SimBrowser(Cookie.SimpleCookie())
        self.UserAgent="Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 2.0.50727; InfoPath.2)";
        self.url_ref = 'htttp://wwww.baidu.com/'
        
        inputT = random.randint(1000,3000)
        rsv_bp, rsv_spt = self.GetBaiduIndex()
        if rsv_bp == -1 or rsv_spt == -1:
            print 'not rsv_bp, rsv_spt'
            return ''

        attrs = {'ie':'utf-8', 'rsv_bp':rsv_bp, 'rsv_spt':rsv_spt, 'inputT':inputT}
        url_attrs = urllib.urlencode(attrs)
        url_domain = 'http://www.baidu.com/s?'
        url = url_domain + url_attrs + '&wd='
        url += key.encode('utf-8')
        #print url

        return self.GetPage(url)

    def GetNextSearchPageLinks(self, html):
        ret = self.base.FindSection(html, '<p id="page">', '</p>')
        if len(ret) != 1:
            return []
        links = self.base.FindSection(ret[0], 'href="', '"')
        #print links
        return links
                
    def GetBaiduNatureLinks(self, key):
        ret = []
        html = self.GetBaiduSearchPages(key, flag_reload=True)
        if html == '':
            #print '---------'
            return ret
        # 得到第一页的搜索结果的links
        ret.extend(self.AnaylsisBdSearchHtml(html))
        #print ret
        # 得到baidu后几页搜索页面的links
        next_pages = self.GetNextSearchPageLinks(html)
        try:
            # 读取后3页搜索页，添加搜索结果的links
            for item in next_pages[:3]:
                full_link = 'http://www.baidu.com' + item.encode('utf-8')
                html = self.GetPage(full_link)
                ret.extend(self.AnaylsisBdSearchHtml(html))
        except:
            pass
        return ret

    def GetBaiduIndex(self):
        res, content = self.sim.request('http://www.baidu.com', 'GET')
        #print res
        if 'status' not in res or res['status'] != '200':
            return -1,-1

        try:
            content = content.decode('gbk')
        except:
            try:
                content = content.decode('utf-8')
            except:
                return -1,-1
            #zreturn -1,-1
        rsv_bp = self.base.FindSection(content, '<input type="hidden" name="rsv_bp" value="', '">')
        if len(rsv_bp) != 1:
            print rsv_bp
            return -1,-1
        rsv_spt = self.base.FindSection(content, '<input type="hidden" name="rsv_spt" value="', '">')
        if len(rsv_spt) != 1:
            print rsv_spt
            return -1,-1        
        try:
            return int(rsv_bp[0]), int(rsv_spt[0])
        except:
            return -1,-1

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
            try:
                if int(rank_id[0]) > 100:
                    continue
            except:
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
        #print table_section[0]
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
            print html_src
            print self.res
            return '0'
        ret = num[0].split(u'约')[1].split(u'个')
        #print ret[0]
        return ret[0]

    def GetBaiduNum(self, key):
        html_src = self.GetBaiduSearchPages(key)
        if html_src == '':
            return '-1'
        return self.GetBaiduPageNum(html_src)

    def find_table(self, html_src, start):
        s = html_src.find('<table', start)
        if s == -1:
            return -1, ''
        e = html_src.find('>', s)
        return e+1, html_src[s:e+1]
    
    def GetBaiduNatureRank(self, key, target_url):
        #links = self.AnaylsisBdSearchHtml(html_src)
        links = self.GetBaiduNatureLinks(key)
        if len(links) == 0:
            return '-1', ''
        for link in links:
            #print link
            # 可能存在的 百度中间页地址
            if link[1].find('http://www.baidu.com/link?url') != -1:
                content = self.base.GetHtmlPage(link[1])
                url = self.base.FindSection(content, 'href="', '"')
                if len(url) == 0:
                    continue
                link[1] = url[0]
            if link[1].find(target_url) != -1:
                return link[0], link[1]
        return '0', ''

    def GetBaiduFixRank(self, key, target_url):
        search_key = key
        html = self.GetBaiduSearchPages(search_key)
        # if couldn't open the url, return -1
        if html == '':
            return '-1',''
        
        link = self.GetFixLink(html)
        for i in xrange(0, len(link)):
            if link[i].find(target_url) != -1:
                return str(i + 1), link[i].split(' ')[0]
        return '0',''

    def GetBaiduFixRank_Cmp(self, key, url_1, url_2):
        search_key = key
        html = self.GetBaiduSearchPages(search_key)
        #print html
        # if couldn't open the url, return -1
        if html == '':
            return '-1','-1'
        
        link = self.GetFixLink(html)
        #print 'fix links', link
        if len(link) == 0:
            return '0', '0'
        ret_1 = 0
        ret_2 = 0
        for i in xrange(0, len(link)):
            if ret_1 == 0 and link[i].find(url_1) != -1:
                ret_1 = i + 1
            elif ret_2 == 0 and link[i].find(url_2) != -1:
                ret_2 = i + 1
        return str(ret_1), str(ret_2)

    def GetBaiduNatureRank_Cmp(self, key, url_1, url_2):
        links = self.GetBaiduNatureLinks(key)
        if len(links) == 0:
            return '-1', '-1'
        ret_1 = '0'
        ret_2 = '0'
        for link in links:
            # 可能存在的 百度中间页地址
            if link[1].find('http://www.baidu.com/link?url') != -1:
                content = self.base.GetHtmlPage(link[1])
                url = self.base.FindSection(content, 'href="', '"')
                if len(url) == 0:
                    continue
                link[1] = url[0]
            if ret_1 == '0' and link[1].find(url_1) != -1:
                ret_1 = link[0]
            elif ret_2 == '0' and link[1].find(url_2) != -1:
                ret_2 = link[0]
        return ret_1, ret_2

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
            #print key, my_url, cmp_url
            if group[5] == 1:
                #my_rank, my_rank_url = self.GetBaiduNatureRank(key, my_url)
                #other_rank, other_rank_url = self.GetBaiduNatureRank(key, cmp_url)
                my_rank, other_rank = self.GetBaiduNatureRank_Cmp(key, my_url, cmp_url)
                # 添加baidu排名情况
                ret.append(my_rank + '|' + other_rank)
                ret.append('|')
                #ret.append(my_rank_url + '|' + other_rank_url)
                #print ret
                #ret.append('')
                google_ranker = getgoogleorder.TGoogleOrder(key.encode('utf-8'), my_url, cmp_url)
                #r_1, r_2 = google_ranker.getFixRank()
                r_1 = 0
                r_2 = 0
                # 添加google排序情况 google没有url
                ret.append(str(r_1) + '|' + str(r_2))
                ret.append('|')
            elif group[5] == 2:
                # 添加百度竞价排名
                #my_rank, my_rank_url = self.GetBaiduFixRank(key, my_url)
                #other_rank, other_rank_url = self.GetBaiduFixRank(key, cmp_url)
                my_rank, other_rank = self.GetBaiduFixRank_Cmp(key, my_url, cmp_url)
                # 添加baidu排名情况
                ret.append(my_rank + '|' + other_rank)
                ret.append('|')
                #ret.append(my_rank + '|' + other_rank)
                #ret.append(my_rank_url + '|' + other_rank_url)
                # google竞价排名为空
                ret.append('|')
                ret.append('|')
            ret.append('unknown flow')
            #ret.append(self.GetBaiduNum(key))
            #ret.append(Get
            #print ret
            #sqlconn.insert_multi(ret, 'rank_compare')
            #print 'sleep for next keyword...'
            #time.sleep(2)
            yield ret

    def thread_rank(self, sqlconn_name):
        sqlconn = sqliteconn.sqlconn(sqlconn_name)
        group_ret = sqlconn.read_group_info('group_info_rank')
        for group in group_ret:
            for key_rank_ret in self.get_rank_of_group(group, sqlconn):
                #print key_rank_ret
                if key_rank_ret[2] == '-1|-1':
                    continue
                sqlconn.insert_multi(key_rank_ret, 'rank_compare')
            #after read a group, sleep for 10 seconds
            #print 'after read a group, sleep for a while...'
            #time.sleep(10)

    def mock_thread_rank(self, sqlconn_name):
        sqlconn = sqliteconn.sqlconn(sqlconn_name)
        group_ret = sqlconn.read_group_info('group_info_rank')
        for group in group_ret:
            for key_rank_ret in self.get_rank_of_group(group, sqlconn):
                print key_rank_ret
            #after read a group, sleep for 10 seconds
            #print 'sleep for next group...'
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
                    #print '---', value, self.url
                    if value.find(self.url) != -1:
                        self.rank = self.ret_tmp
                        self.rank_url = value

def thread_rank(sqlconn_name):
    rank_getter = GetBaiduRank()
    rank_getter.thread_rank(sqlconn_name)

if __name__ == '__main__': 
    rank_getter = GetBaiduRank()
    #rank_getter.GetPage('http://www.baidu.com/link?url=a0dc9c4ab66b234c1c69e829ee96ee81a6e8c0962218c9e338d199d3aad4553b3042aeb663c4a7916db70b8e72a5ca4845b14052ba6a99e563e92829b2c3025698353893')
    while True:
        #rank_getter = GetBaiduRank()
        rank_getter.thread_rank('company.db')
        #print rank_getter.GetBaiduLinks(u'鲜花')
        #break
    #pass
    #while True:
        #rank_getter.thread_rank('company.db')
    #thread_rank('company.db')
    #print GetBaiduPageFull('鲜花', 'bj.58.com')
    #print GetBaiduFixRank('鲜花', 'zhenaihuawu.com')
    #thread_rank()
    #thread_query()
    #GetBaiduNum(u'鲜花')
