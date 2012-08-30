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

class GetBaiduRank():
    def __init__(self):
        self.base = Base.Base()

    def GetPage(self, url):
        header = {'Referer':self.url_ref,'User-Agent':self.UserAgent}    
        res,Fhtml = self.sim.request(url,'GET',headers=header);

        # 如果 response 为空或者状态不对 返回''
        if 'status' not in res or res['status'] != '200':
            return ''
        # 更新url ref
        self.url_ref = url
        # 尝试解码网页。解码格式为utf-8 和 gbk
        try:
            content = Fhtml.decode('utf-8')
        except:
            try:
                content = Fhtml.decode('gbk')
            except:
                content = ''

        return content

    def GetBaiduSearchPages(self, key, flag_reload=True):
        # 每次抓取一个key， 复原http的信息
        self.sim = SimHttp.SimBrowser(Cookie.SimpleCookie())
        self.UserAgent="Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 2.0.50727; InfoPath.2)";
        self.url_ref = 'htttp://wwww.baidu.com/'
        
        inputT = random.randint(1000,3000)
        # 读取百度首页，模拟网页搜索过程。抓取参数。
        rsv_bp, rsv_spt = self.GetBaiduIndex()
        # 如果解析参数失败，返回空
        if rsv_bp == -1 or rsv_spt == -1:
            return ''

        # 拼接要搜索的url
        attrs = {'ie':'utf-8', 'rsv_bp':rsv_bp, 'rsv_spt':rsv_spt, 'inputT':inputT}
        url_attrs = urllib.urlencode(attrs)
        url_domain = 'http://www.baidu.com/s?'
        url = url_domain + url_attrs + '&wd='
        url += key.encode('utf-8')

        return self.GetPage(url)

    def GetNextSearchPageLinks(self, html):
        '''读取搜索结果第一页中存在的后续搜索结果页的url，前10条为有效页'''
        ret = self.base.FindSection(html, '<p id="page">', '</p>')
        if len(ret) != 1:
            return []
        links = self.base.FindSection(ret[0], 'href="', '"')
        return links
                
    def GetBaiduNatureLinks(self, key):
        '''返回一个关键字对应搜索得到的url'''
        ret = []
        html = self.GetBaiduSearchPages(key, flag_reload=True)
        if html == '':
            #print '---------'
            return ret
        # 得到第一页的搜索结果的links
        ret.extend(self.AnaylsisBdSearchHtml(html))
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
        '''打开百度首页，解析得到搜索页中的参数'''
        res, content = self.sim.request('http://www.baidu.com', 'GET')
        if 'status' not in res or res['status'] != '200':
            return -1,-1

        try:
            content = content.decode('gbk')
        except:
            try:
                content = content.decode('utf-8')
            except:
                return -1,-1

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
        '''分析一个搜索页，得到其中的自然结果的link和对应的排名'''
        table_ret = self.base.FindSection(html, '<table', '>')
        ret = []
        for table in table_ret:
            rank_id = self.base.FindSection(table, 'id="', '"')
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
        return left_rank

    def GetBaiduPageNum(self, html_src):
        '''解析搜索页中的收录量'''
        num = self.base.FindSection(html_src, '<span class="nums"', '</span>')
        if len(num) != 1:
            return '0'
        ret = num[0].split(u'约')[1].split(u'个')
        return ret[0]

    def GetBaiduNum(self, key):
        '''得到百度收录量'''
        html_src = self.GetBaiduSearchPages(key)
        if html_src == '':
            return '-1'
        return self.GetBaiduPageNum(html_src)

    def GetBaiduNatureRank(self, key, target_url):
        links = self.GetBaiduNatureLinks(key)
        if len(links) == 0:
            return '-1', ''
        for link in links:
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
        # if couldn't open the url, return -1
        if html == '':
            return '-1','-1'
        
        link = self.GetFixLink(html)
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
        '''如果是www.xxx.com，则获取他的host'''
        if url.find('www.') != -1:
            return url.replace('www.', '.')
        return url

    def get_rank_of_group(self, group, sqlconn):
        keywords = group[2].split('#')
        for key in keywords:
            ret = [str(group[0]), key]
            # 得到url的host作为对应的查询url
            my_url = self.GetHost(group[3])
            cmp_url = self.GetHost(group[4])
            if group[5] == 1:
                my_rank, other_rank = self.GetBaiduNatureRank_Cmp(key, my_url, cmp_url)
                # 添加baidu排名情况
                ret.append(my_rank + '|' + other_rank)
                ret.append('|')
                # 添加google排序情况 
                google_ranker = getgoogleorder.TGoogleOrder(key.encode('utf-8'), my_url, cmp_url)
                r_1, r_2 = google_ranker.getFixRank()
                ret.append(str(r_1) + '|' + str(r_2))
                ret.append('|')
            elif group[5] == 2:
                # 添加百度竞价排名
                my_rank, other_rank = self.GetBaiduFixRank_Cmp(key, my_url, cmp_url)
                ret.append(my_rank + '|' + other_rank)
                ret.append('|')
                # google竞价排名为空
                ret.append('|')
                ret.append('|')
            ret.append('unknown flow')
            yield ret

    def thread_rank(self, sqlconn_name):
        sqlconn = sqliteconn.sqlconn(sqlconn_name)
        group_ret = sqlconn.read_group_info('group_info_rank')
        for group in group_ret:
            for key_rank_ret in self.get_rank_of_group(group, sqlconn):
                # 如果百度排名查询失败，则返回
                if key_rank_ret[2] == '-1|-1':
                    continue
                #print key_rank_ret
                sqlconn.insert_multi(key_rank_ret, 'rank_compare')

    def mock_thread_rank(self, sqlconn_name):
        sqlconn = sqliteconn.sqlconn(sqlconn_name)
        group_ret = sqlconn.read_group_info('group_info_rank')
        for group in group_ret:
            for key_rank_ret in self.get_rank_of_group(group, sqlconn):
                print key_rank_ret

def thread_rank(sqlconn_name):
    rank_getter = GetBaiduRank()
    rank_getter.thread_rank(sqlconn_name)

if __name__ == '__main__': 
    rank_getter = GetBaiduRank()
    while True:
        rank_getter.thread_rank('company.db')
