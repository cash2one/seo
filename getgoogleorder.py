# -*-coding:utf-8 -*-
"""
  google 排名接口类

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

import SimHttp;

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
def GetgoogleList(aHtml,aCysTag,TitleTag,TitleFt,TitleEnd): # 获取goole 当页 list
    aList=[]
    if aHtml.find(aCysTag)>0:
        tempStr = aHtml
        while tempStr!='':
            index = tempStr.find(aCysTag);
            if index==0:
                tempStr = '';
                continue;
            else:
                tempStr = tempStr[index:len(tempStr)];
                
            aTitle = gethtmltagval(tempStr,TitleTag,TitleFt,TitleEnd);
            if aTitle=='<span class':
                aTitle = gethtmltagval(tempStr,'href="','','"',false);
            if aTitle.find('...')>0:
                aTitle = gethtmltagval(tempStr,'href="/url?','http://','&amp;',false);
            if aTitle.find('href="/url?')>0:
                aTitle = gethtmltagval(tempStr,'href="/url?','http://','&amp;',false);
                
            aList.append(aTitle);

            tempStr = tempStr[len(aCysTag)+1:len(tempStr)];
            
    return aList;
 
class TGoogleOrder:
    """
    TGoogleOrder 谷歌排名接口类     
    """
    FHost1 = '';
    FHost2 = '';
    FkeyStr = '';
    FList=[];#谷歌的 url list
    UserAgent="Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 2.0.50727; InfoPath.2)";
    cookie = Cookie.SimpleCookie();
    sim = SimHttp.SimBrowser(cookie);    
    def __init__(self,KeyStr='',aHost1='',aHost2=''):
        """
          aHost 网站主域名
        """
        self.FHost1 = aHost1;
        self.FHost2 = aHost2;
        self.FkeyStr = KeyStr;
        
    def getFixRank(self): #获取排名
        re1 = 0
        re2 = 0
        j = 0
        index =0
        aUrl = 'http://www.google.com.hk/';
        self.sim.request(aUrl,'GET');
        
        for i in range(3):            
            if i==0:
                aUrl = 'http://www.google.com.hk/search?hl=zh-CN&safe=strict&q='+self.FkeyStr;
                Refer ='http://www.google.com.hk/';
            else:
                Refer=aUrl;
                aUrl = 'http://www.google.com.hk/search?hl=zh-CN&safe=strict&q='+self.FkeyStr+'&start='+str(10*i);
            

            header = {'Referer':Refer,'User-Agent':self.UserAgent}    
            res,Fhtml = self.sim.request(aUrl,'GET',headers=header);

            if len(Fhtml)== 0:
                return -1,-1;
            
            aPageCycHtml = gethtmltagval(Fhtml,'<div id="res">','','相关搜索');
            if aPageCycHtml=='':
               aPageCycHtml = gethtmltagval(Fhtml,'class="hd">搜索结果','','相关搜索');

            if Fhtml.find('<div id="res">')>0:
                self.Flist = GetgoogleList(aPageCycHtml,'<li class="g">','<cite>','','</cite>');
            else:
                self.Flist = GetgoogleList(aPageCycHtml,'<li class="g">','href="','','"');
            index =0;
            for listurl in self.Flist:
                #print listurl;
                index = index +1;
                j = i * 10 +index; 
                if re1 == 0 and listurl.find(self.FHost1)>0:
                    re1=j
                if re2 == 0 and listurl.find(self.FHost2)>0:
                    re2=j 
            if re1>0 and re2>0:
                break;
        return re1,re2            
                
def main():
    GoogleOder = TGoogleOrder('笔记本','pconline.com','zol.com');
    print GoogleOder.getFixRank();
        

if __name__ == "__main__":
    main(); 
                
                
            
