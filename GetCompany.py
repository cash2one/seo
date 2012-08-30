# -*-coding:utf-8 -*-

import HTMLParser
import urllib
import re
import string
import sqliteconn
import SimHttp
#import PrBdkey
import time
import Cookie

cookie = Cookie.SimpleCookie()
sim = SimHttp.SimBrowser(cookie)

class FindUrlParser(HTMLParser.HTMLParser):
    ''' '''
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.flag = False
        self.sug = ''

    def handle_starttag(self, tag, attrs):
        HTMLParser.HTMLParser.handle_starttag(self, tag, attrs)
        if 'a' == tag:
            if ('class','l') in attrs:
                for key,value in attrs:
                    if key == 'href':
                        self.sug = value
            else:
                self.sug = ''
                     
def erase_other(line):
    s = line.find('<')
    e = line.find('>', s)
    return line[0:s] + line[e + 1:]

def ParserDetailHtml(html_src):
    '''解码页面，得到详细信息'''
    s_pos = html_src.find(u'[更新')
    if s_pos == -1:
        return []
    e_pos = html_src.find(']')

    date = time.localtime(time.time())
    date = time.strftime('%Y-%m-%d', date)
    # 查看网页中的更新时间信息，如果不是当前不要
    if html_src[s_pos + 4:e_pos] != date:
        return []
    dic = [html_src[s_pos + 4:e_pos]]
    s_pos = html_src.find('<DIV class=mainintxt>')
    if s_pos == -1:
        return []
    e_pos = html_src.find('</DIV>', s_pos)
    all_detail = html_src[s_pos + len('<div class=mainintxt>') + 1: e_pos]
    all_detail = all_detail.strip('</UL>').strip('<UL>')
    items = all_detail.split('\n')

    for i in items:
        if i.find('<LI>') != -1:
            t = i.strip().replace('<LI>','').replace('</LI>','')
            t = t.replace('<SPAN>','').replace('</SPAN>','')
            while t.find('<') != -1:
                t = erase_other(t)
            if t.find('&nbsp;') != -1:
                t = t[0:t.find('&nbsp;')]
            k_v = t.split(':')
            dic.append(k_v[1])

    return dic

def ReadYouboyHtml(url, pre_url):
    re, content = sim.request(url, 'GET')
    return content

def ReadDetailHtml(url, pre_url):
    full_url = 'http://www.youboy.com' + url
    html_src = ReadYouboyHtml(full_url, pre_url)
    try:
        html_src = html_src.decode('utf-8')
    except:
        return []
    return ParserDetailHtml(html_src)

def FindTagA(html_src, start):
    s = html_src.find('<A', start)
    if s == -1:
        return -1, ''
    e = html_src.find('>', s)

    return e+1, html_src[s:e+1]

def ReadSearchHtml(html_src):
    '''解析搜索结果页，返回详细信息url'''
    htmlparser = FindUrlParser()
    idx = 0
    ret = []
    while True:
        idx, content = FindTagA(html_src, idx)
        if idx == -1:
            break
        htmlparser.feed(content)
        if htmlparser.sug != '':
            ret.append(htmlparser.sug)
    return ret

def ReadHtmlOnPage(key, pagenum=0):
    attrs = {'s':'2', 'p':'0'}
    attrs['p'] = str(pagenum)
    url_attrs = urllib.urlencode(attrs)
    url_domain = 'http://www.youboy.com/s/s.jsp?'
    url = url_domain + url_attrs + '&kw='
    url += key.encode('utf-8')
    html_src = ReadYouboyHtml(url, '')
    ret = []
    for item in ReadSearchHtml(html_src):
        dic = [key]
        dic.extend(ReadDetailHtml(item, url)) 
        # read a html then sleep for 5 seconds...
        time.sleep(5)
        if len(dic) == 1:
            continue
        ret.append(dic)
    return ret

def CrawlerHtml(key, max_page=2):
    '''返回 company 信息的结果列表'''
    search_key = key
    for i in xrange(0,max_page):
        yield ReadHtmlOnPage(search_key, i + 1)

def main():
    CrawlerHtml('笔记本', 3)

def get_company_of_group(group, sqlconn):
    keys = group[2].split('#')
    for key in keys:
        for item in CrawlerHtml(key, 3):
            for dic in item:
                ist = [str(group[0])]
                ist.extend(dic)
                sqlconn.insert(ist, 'company')

def thread_crawler_company(sqlconn_name):
    sqlconn = sqliteconn.sqlconn(sqlconn_name)
    group_ret = sqlconn.read_group_info('group_info_company')
    for group in group_ret:
        get_company_of_group(group,sqlconn)
        time.sleep(10)

if __name__ == '__main__':
    #main()
    thread_crawler_company()
