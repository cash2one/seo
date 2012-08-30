# -*-coding:utf-8 -*-
"""
  TAizhanFace 新浪微博http接口类

"""
import sys
import os
import urllib2;
import httplib2;
import Cookie;
import random;
import re;
import json;
import time;
import sqliteconn

import SimHttp;

#httplib2.debuglevel=1;
   

def random_num(num): # 随机获取 指定 num 个数的 数字字符串
    result='';
    for i in range(0, num):
        result = result + str(random.randint(0, 9));
    return result;

def getjstimestr(time): # 获取 格林时间 字符串
    
    timestr=str(time);
    index=timestr.find('.');
    if index>0:
        tstr=timestr[0:index]
    else:
        tstr=timestr;
    return tstr+random_num(3);



#---------获取字符中 atag ,start end 之间的字符串---------
def gethtmltagval(html,atag,start,end):
    t = html.find(atag);
    if (t >= 0):
        if (start <> ''):
            aparthtml = html[t+len(atag):len(html)]
            s = aparthtml.find(start)
            if s < 0:
                return '';
            aparthtml = aparthtml[s+len(start):len(html)]
            e = aparthtml.find(end)
            if e < 0:
                return '';
            return aparthtml[0:e]
        else:
            aparthtml = html[t+len(atag):len(html)]
            e = aparthtml.find(end)
            return aparthtml[0:e]            
    else:
        return '';

class TaizhanFace:
    """
    aizhan http接口类
     
    """
    aHost = ''
    cc = ''    
    UserAgent="Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 2.0.50727; InfoPath.2)";
    cookie = Cookie.SimpleCookie();
    sim = SimHttp.SimBrowser(cookie);    
    def __init__(self, aHost=''):
        """
         aHost 网站主域名
        """
        self.aHost = aHost;
    def getwebinfo(self):
        '''返回 ip,页内连接，三月排名，ip访问，pv访问，网页标题，网页关键字，网页描述，pr，电信访问速度，联通访问速度'''
        aUrl ='http://www.aizhan.com/siteall/'+self.aHost;
        header ={'User-Agent':self.UserAgent};
        res, content = self.sim.request(aUrl,'GET',headers=header,follow_redirects=True);
        content = content.decode('utf-8')
        self.cc = gethtmltagval(content,"key_domain =","'","'");
        aIP = gethtmltagval(content,"var url_ip =","'","'");
        seoOutlink = gethtmltagval(content,'id="seo_link"',u'出站链接：',u'个');
        seoInlink = gethtmltagval(content,'id="seo_link"',u'首页内链：',u'个');
        aveThree = gethtmltagval(content,'id="alexa_3months"','>','</');
        aALEXAIP = gethtmltagval(content,'id="alexa_IPPV">IP','; ','PV');
        aALEXAUV = gethtmltagval(content,'id="alexa_IPPV"','PV&asymp;','</');
        webtitle = gethtmltagval(content,'id="webpage_title">','','</td>');  # 网站标题
        webkeys = gethtmltagval(content,'id="webpage_keywords">','','</td>');# 网站关键词
        webdesc = gethtmltagval(content,'id="webpage_description">','','</td>'); # 网站描述
        aPr = gethtmltagval(content,'images/pr/pr','','.gif'); # Pr查询
        adianxiRun = gethtmltagval(content,u'电信响应：','','&n');
        aliantongRun = gethtmltagval(content,u'联通响应：','','"');

        return [aIP,seoInlink,aveThree,aALEXAIP,aALEXAUV,webtitle,webkeys,webdesc,aPr,adianxiRun ,aliantongRun]

        
    def getbaiduip(self):
        timestr=getjstimestr(time.time())[0:9];        
        aUrl = 'http://www.aizhan.com/getbrinfo.php?url='+ self.aHost+'&_'+timestr;
        print aUrl;
        header ={'User-Agent':self.UserAgent};
        res, content = self.sim.request(aUrl,'GET',headers=header,follow_redirects=True);
        content = content.decode('utf-8')
        return [gethtmltagval(content,'baidu_ip','"','"')];
    def getoutlink(self): #  获取外链个数
        timestr=getjstimestr(time.time())[0:9]; 
        aUrl = 'http://www.aizhan.com/ajaxAction/backlink1.php?domain='+self.aHost+'&rn='+timestr+'&cc='+self.cc;
        print aUrl;
        header ={'User-Agent':self.UserAgent};
        res, content = self.sim.request(aUrl,'GET',headers=header,follow_redirects=True);
        return [content];
    def getSeverInfo(self):
        timestr=getjstimestr(time.time())[0:9];
        aUrl = 'http://www.aizhan.com/ajaxAction/dns.php?domain='+self.aHost+'&rn='+timestr+'&cc='+self.cc;

        print aUrl;
        header ={'User-Agent':self.UserAgent};
        res, content = self.sim.request(aUrl,'GET',headers=header,follow_redirects=True);
        address = gethtmltagval(content,'"address":"','','"');
        WebNum = gethtmltagval(content,'"num":"','','"');
        return address,WebNum  #服务器所在地，运行几个网站
    
    def getshoulu(self): # 获取收录
        timestr=getjstimestr(time.time())[0:9];
        aUrl = 'http://www.aizhan.com/ajaxAction/shoulu1.php?domain='+self.aHost+'&rn='+timestr+'&cc='+self.cc;
        print aUrl;
        header ={'User-Agent':self.UserAgent};
        res, content = self.sim.request(aUrl,'GET',headers=header,follow_redirects=True);
       #content = {"baidu":"61,900,000","aagoogle":"100000"}
        print content
        return gethtmltagval(content,'baidu":"','','"'),gethtmltagval(content,'google":"','','"');
    def getshoululink(self): # 获取反向链接
        timestr=getjstimestr(time.time())[0:9];
        aUrl = 'http://www.aizhan.com/ajaxAction/shoulu2.php?domain='+self.aHost+'&rn='+timestr+'&cc='+self.cc;
        print aUrl;
        header ={'User-Agent':self.UserAgent};
        res, content = self.sim.request(aUrl,'GET',headers=header,follow_redirects=True);
        #{"baidu_r":"100,000,000","google_r":"9,350"}
        print content;
        return gethtmltagval(content,'baidu_r":"','','"'),gethtmltagval(content,'google_r":"','','"')

def get_diagnose_of_url(url):
    getter = TaizhanFace(url)
    ret = getter.getwebinfo()
    ret.extend(getter.getoutlink())
    ret.extend(getter.getbaiduip())

    return ret

def get_diagnose_of_group(group, sqlconn):
    if group[4] != 0:
        return False
    
    ret_my = get_diagnose_of_url(group[2])
    ret_other = get_diagnose_of_url(group[3])

    ret = [str(group[0])]
    for i in xrange(0,len(ret_my)):
        ret.append(ret_my[i] + '|' + ret_other[i])

    #print len(ret)
    sqlconn.insert_multi(ret, 'diagnose')
    #更新状态为 诊断结束
    ret_dic = {'status':'1'}
    s_dic = {'groupid':str(group[0])}
    sqlconn.update_table(ret_dic, s_dic, 'group_info_diagnose')
    return True

def thread_diagnose(sqlconn_name):
    sqlconn = sqliteconn.sqlconn(sqlconn_name)
    #print 'ok'
    group_ret = sqlconn.read_group_info('group_info_diagnose')
    for group in group_ret:
        if get_diagnose_of_group(group, sqlconn):
            time.sleep(10)
    #print 'finish'
    
def main():
    atest = TaizhanFace('163.com');
    for item in atest.getwebinfo():
        print item
    print atest.getbaiduip();  #百度预感流量
    print atest.getoutlink()   #外链
    #print atest.getSeverInfo(); 
    #atest.getshoulu() 
    #atest.getshoululink()
        

if __name__ == "__main__":
    #main();
    thread_diagnose('company.db')
