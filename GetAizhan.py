# -*-coding:utf-8 -*-

# 抓取爱站的信息

import sqliteconn
import PrBdkey

def ReadAizhanHtml(url):
    sim = PrBdkey.SimBrowser('', PrBdkey.GetRandUserAgent())
    head = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset':'GBK,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding':'gzip,deflate,sdch',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Cache-Control':'max-age=0',
            'Cookie':'defaultSiteState=1; baidurankSite=www.youboy.com; siteallSite=www.youboy.com; allSites=www.youboy.com%2C1%7Cifshall.com%7Cif4ever.com%7Cwww.365flower.com.cn',
            'Host':'www.aizhan.com',
            'Referer':'http://www.aizhan.com/'}
    request_url = 'http://www.aizhan.com/siteall/' + url
    print request_url
    re, content = sim.request(request_url, 'GET', headers=head)
    print content

if __name__ == '__main__':
    ReadAizhanHtml('www.baidu.com')
    
