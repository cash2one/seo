# -*-coding:utf-8 -*-

# 抓取爱站的信息

import sqliteconn
import PrBdkey
import urllib
import BaiduRank

def GetKeyWord(src):
    ret = BaiduRank.FindSection(src, '<font color=#0269AC>', '</font>')
    for key in ret:
        print '#',key
    #s_k = src.find('>')

def GetItemInfo(src):
    ret = BaiduRank.FindSection(src, '<tr class="seo_item">', '</tr>')
    for item in ret:
        key_words = BaiduRank.FindSection(item, '<td', '</td>')
        for key in key_words:
            if key.strip() != '':
                #print '--',key
                GetKeyWord(key)
        #print item

def GetInfoTable(html):
    ret = BaiduRank.FindSection(html, '<table class="seo"  cellpadding="5" cellspacing="1" id="seoinfo">', '</table>')
    #for item in ret:
    #    print item
    GetItemInfo(ret[0])

def ReadAizhanHtml(url):
    sim = PrBdkey.SimBrowser('', PrBdkey.GetRandUserAgent())
    head = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset':'GBK,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding':'gzip,deflate,sdch',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Cache-Control':'max-age=0',
            'Cookie':'',
            'Referer':'http://tool.chinaz.com/'}
    request_url = 'http://seo.chinaz.com/?q=' + url
    print request_url
    #re, content = sim.request(request_url, 'GET', headers=head)
    #print content

    html_src = urllib.urlopen(request_url).read()
    #print html_src
    #return content.decode('utf-8')
    return html_src.decode('utf-8')

def main():
    #html_src = ReadAizhanHtml('www.baidu.com')
    html_src = open('3.txt').read()
    #print html_src
    GetInfoTable(html_src)

if __name__ == '__main__':
    main()
    
