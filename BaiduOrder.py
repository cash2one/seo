#!/usr/bin/python
# -*-coding:utf-8 -*-
import sys;
import os;
import urllib2;
import httplib2;
import Cookie;
import random;
import re;
import json;
import time;
from urllib import urlencode;
import hashlib;
import datetime;
import socket
#httplib2.debuglevel=1;

def error_log(log):
    sys.stderr.write("%s\n" % (log));

class ErrorCode:
    Succ         = 0;
    Unknown      = -1; # 未知原因
    AccFrozen    = 1;  # 账户冻结

class SimBrowser :
    socket.setdefaulttimeout(10); # 超时限制 10秒
    UserAgent="";
    cookie=None;
    httplink = httplib2.Http();    
    httplink.follow_redirects = False;
    
    def __init__(self, cookie, UserAgent="Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 2.0.50727)"):
        self.cookie = cookie;
        self.UserAgent = UserAgent;        
        
    def gen_cookie_str(self):
        cookiestr = '; '.join(self.cookie.output(attrs=[], header="").split('\r\n'));
        if len(cookiestr) <= 0:
            return "";
        else:
            return cookiestr;
    def prepare_request_header(self, header):
        newheader = {};
        cookiestr = self.gen_cookie_str();
        if len(cookiestr) > 0:
            newheader['Cookie'] = cookiestr;        
        # set agent
        newheader['User-Agent'] = self.UserAgent;
        
        # replace or append user specified values in header
        for key in header.keys():
            newheader[key] = header[key];
        return newheader;

    # maintain cookies
    def maintain_cookie(self, response_header):
        if 'set-cookie' in response_header:
            self.cookie.load(response_header['set-cookie']);            

    def get_redirect_url(self, prevurl, res):
        if 'location' not in res:
            error_log('no location in res');
            return "";

        location = res['location'];
        if len(location) <= 0:
            error_log('location length is zero');
            return "";

        # check location contain fullpath of target
        if location.find("http://") != 0:
            p = re.compile(r"[(http://)]*[.\-_0-9A-Za-z]+");
            m = p.match(prevurl);
            if m != None:                
                host = m.group();
                return host + location;
            else:
                error_log('cannot get host link');
                host = "";
        else:
            return location;

    def request(self, url, method="GET", headers={}, body="", follow_redirects=False): 
        newheaders = self.prepare_request_header(headers);
        newurl = url;
        newbody = body;
        while (True):
            try:
              res, content = self.httplink.request(newurl, method=method, headers=newheaders, body=newbody);
              self.maintain_cookie(res);
            except Exception , what:
                try:
                  res, content = self.httplink.request(newurl, method=method, headers=newheaders, body=newbody);
                  self.maintain_cookie(res);
                except Exception , what: 
                    try:
                      res, content = self.httplink.request(newurl, method=method, headers=newheaders, body=newbody);
                      self.maintain_cookie(res);
                    except Exception , what: # 访问获取 三次 不成功返回失败
                        res='';
                        content='';
                        break;

            # check redirects
            if follow_redirects==False:
                break;
            elif res.status in(300, 301, 302):                
                prevurl = newurl;
                newheaders = self.prepare_request_header({});
                newurl = self.get_redirect_url(prevurl, res);
                body = "";
                method="GET";
                if len(url) > 0:
                    continue;
                else:
                    sys.stderr.write("Error:failed to get redirect location\n");
                    break;
            else:
                break;
        return res, content;

def random_num(num):
    result='';
    for i in range(0, num):
        result = result + str(random.randint(0, 9));
    return result;
def getDateStr(num): #num 为加减日期 格式为:'yyyy-mm-dd';
    today=datetime.date.today();
    oneday = datetime.timedelta(days=abs(num));
    if num>0:
        returnday=today+oneday;
    else:
        returnday=today-oneday;
    return str(returnday);

def getjstimestr(time):
    timestr=str(time);
    index=timestr.find('.');
    if index>0:
        tstr=timestr[0:index]
    else:
        tstr=timestr;
    return tstr+random_num(3);
#----------- htmlencode-------
def htmlcode(s):
    s=s.replace('&','&amp;');
    s=s.replace('<','&lt;');
    s=s.replace('>','&gt;');
    s=s.replace('"','&quot;');
    s=s.replace('\'','&apos;');
    return s;


#---------获取字符中 atag ,start end 之间的字符串---------
def gethtmltagval(html,atag,start,end):
    t=html.find(atag);
    result='';
    if (t>=0):
        if (start != ''):
            aparthtml=html[t+len(atag):len(html)]
            s=aparthtml.find(start)
            aparthtml=aparthtml[s+len(start):len(html)]
            e=aparthtml.find(end);
            result=aparthtml[0:e];
            if result==None:
                result='';
            return result;
        else:
            aparthtml=html[t+len(atag):len(html)]
            e=aparthtml.find(end);
            result=aparthtml[0:e];
            if result==None:
                result='';
            return result;            
    else:
        return '';
def gethtmltagpostionval(ahtml,atag,start,end): # atag 前面的标识字识 position True;
    index=ahtml.find(atag);
    if index>=0:
        tempStr=ahtml[0:index];
        ln=len(tempStr);
        if end=='': #直接就是
            for i in range(ln):
                aStr=tempStr[-i-1:ln];
                if aStr.find(start)==0:
                    aStr=aStr[len(start):len(aStr)];
                    if aStr==None:
                        aStr='';
                    return aStr;
            return '';
        else:
            for i in range(ln):
                aStr=tempStr[-i-1:ln];
                if aStr.find(start)==0:
                    aStr=aStr[len(start):len(aStr)];
                    aEindex=aStr.find(end);
                    aStr=aStr[0:aEindex];
                    if aStr==None:
                        aStr='';
                    return aStr;
            return '';
    else:
        return '';
                    
def GetHtmltxt(html):# 获取html 纯文本
    from HTMLParser import HTMLParser;
    html=html.strip()
    html=html.strip("\n")
    result=[]
    parse=HTMLParser()
    parse.handle_data=result.append
    parse.feed(html)
    parse.close()
    return "".join(result);

def GetEleValByRef(aRefStr,aElementStr):
    #tempStr=aElementStr.lower();
    #aRefStr=aRefStr.lower();
    index=aElementStr.find(aRefStr);
    if index==0:
        return '';
    reStr=gethtmltagval(aElementStr,aRefStr+'\"','','\"');
    if reStr=='':
        reStr=gethtmltagval(aElementStr,aRefStr+'\'','','\'');
    return reStr;    
    
    
def GethrefTitle(aHrefStr):#获取 超链接中 标题    
    index=aHrefStr.find('>');
    endindex=aHrefStr.find('</a>');
    if index==0 or endindex==0:
        return '';
    tempStr=aHrefStr[index+1:endindex]+'</a>';
    tempStr=GetHtmltxt(tempStr);
    if tempStr=='':
        return GetEleValByRef('name=',aHrefStr);
    else:
        return tempStr;
    
    
def GetHrefHtml(aHtml,aHrefTag,Position): #获取<a href=''>sdf</a> 标签
    index=aHtml.find(aHrefTag);
    if index==0:
        return '';
    aHtml=aHtml.replace('<A','<a');
    if Position==True:
        TempStr=gethtmltagpostionval(aHtml,aHrefTag,'<a ','');
        reStr=gethtmltagval(aHtml,aHrefTag,'','</a>');
        return '<a '+TempStr+aHrefTag+reStr+'</a>';
    else:
        TempStr=aHtml[index-1:len(aHtml)];
        return '<a '+gethtmltagval(TempStr,'<a ','','</a>')+'</a>';
    
def GetHrefTitleValList(aHtml,aCysTag,aHrefTag,Position): #获取标准备的超链接
    aTitleList=[];
    i=aHtml.find(aCysTag);
    if i>0:
        tempStr=aHtml;
        while tempStr!='':
            filedStr='';
            index=tempStr.find(aCysTag);
            if index==0:
                tempStr='';
                break;
            else:
                if Position==False:
                    tempStr=tempStr[index:len(tempStr)];
            if aHrefTag=='':
                fieldStr=GetHrefHtml(tempStr,aCysTag,False);
            else:
                fieldStr=GetHrefHtml(tempStr,aHrefTag,True);
            
            if fieldStr!='' and fieldStr!=None:
                aTitle=GethrefTitle(fieldStr);
                aUrl=GetEleValByRef('href=',fieldStr);
                aUrl=aUrl.replace('&amp;','&');
                if aTitle=='':
                    aTitle=GetEleValByRef(aHrefTag,fieldStr);
                    aTitle=aTitle.replace('&amp;','&');
                    aTitle=aTitle.replace('&lt;','<');
                    aTitle=aTitle.replace('&gt;','>');
                    aTitle=aTitle.replace('&quot;','"');
                    aTitle=aTitle.replace('&ldquo;','“');
                    aTitle=aTitle.replace('&rdquo;','”');
                    aTitle=aTitle.replace('&nbsp;',' ');
                aTitle=aTitle.replace('\t','');
                aTitle=aTitle.replace('\r','');
                aTitle=aTitle.replace('\n','');
                aTitle=aTitle.replace('	','');
                if aTitle!='' and aTitle!=None:
                    aTitleList.append(aTitle+'\t'+aUrl);
                if Position==True:
                    tempStr=tempStr[tempStr.find(aCysTag)+len(aCysTag):len(tempStr)];
                    if tempStr.find(aCysTag)==0:
                        break;
                else:
                    tempStr=tempStr[len(aCysTag)+len(fieldStr):len(tempStr)];
            else:
                break;           
    return aTitleList;

def HasInArea(Num,StartNum,EndNum):
    if StartNum>EndNum:
        if Num>EndNum and Num<StartNum:
            return True;
    else:
        if Num>StartNum and Num<EndNum:
            return True;
    return False;
def GetAveSetPrice(ActivePrice,LastSetPrice,aActiveOrder,LastOrder,LeftCount,RigthCount): #获取该词的快速调整
    if LastSetPrice==0:# 表明该词是刚调整
        if RigthCount==0: #防止为0
            RigthCount=1;
        if aActiveOrder<20:
            return float(ActivePrice)/(LeftCount-aActiveOrder+RigthCount); #理论是当前出价减 最低展现价 省一步最低展现价
        else:
            return float(ActivePrice)/(RigthCount);  #在右边提升的空间大
    else:
        if LastOrder==0: #没有排名 上次出价不是没有排名
            return LastSetPrice*1.2; # 添加 1.2 比例空间       
        
        if aActiveOrder==LastOrder:  #本次排名相同，说明要还要加价调整
            return LastSetPrice*1.2; #添加 1.2比例上调            
        else:#本次排名不于上次相同
            if aActiveOrder<20 and LastOrder<20 : #都排在左边
                try:
                    Result=abs(float(LastSetPrice)/(aActiveOrder-LastOrder));
                except:
                    result=0.1;                    
            elif aActiveOrder<20 and LastOrder>20:
                try:
                    Result=abs(float(LastSetPrice)/(LastOrder-20+LeftCount-aActiveOrder));
                except:
                    Result=0.1;
            elif aActiveOrder>20 and LastOrder<20:
                try:
                    Result=abs(float(LastSetPrice)/(aActiveOrder-20+LeftCount-LastOrder));
                except:
                    Result=0.1;                
            elif aActiveOrder>20 and LastOrder>20:
                try:
                    Result=abs(float(LastSetPrice)/(aActiveOrder-LastOrder));
                except:
                    Result=0.1;
            else:
                Result=0.1;
    return Result;
    
        
def GetAdjustPrice(aSetOrder,aActiveOrder,ActivePrice,LastOrder,LastSetPrice,StepVal,LeftCount,RigthCount): #获取调整价格
    #aSetOrder 要调的排名 aActiveOrder 当前排名, ActivePrice 当前出价(算初始值用) lastOrder 上次排名  LastSetPrice 上次调价 StepVal 调价幅度 leftCount 左侧当前竞价个数 rigthCount 右侧当前竞价个数
    aRealOrder=0;
    if aSetOrder==11: #表明要调到左侧 1-3 位置
        aRealOrder=2;
    elif aSetOrder==12: #表明要调到左侧 4-6位置
        aRealOrder=5;
    else:
        aRealOrder=aSetOrder; #目标排名
    if LeftCount==0: #左侧没有排名
        aRealOrder=21;  #目标排名只能为右侧第一
    if LeftCount>0 and aSetOrder<21:
        if aSetOrder>LeftCount:
            aRealOrder=LeftCount; #目标排名为 左侧最低展现
    if aSetOrder>20:
        if aSetOrder>(20+RigthCount):
            aRealOrder=20+RigthCount; # 目标排名为最右侧最低展现价
            
    if aActiveOrder==0: #表明该词还没有展现 需要最低展现价格 + 调价幅度 . 历史的数据是否要加上
        if StepVal==0:  #初始值
            StepVal=0.1;
        if aRealOrder<20: #表明目标排名在排在左边
            if StepVal>0: #表明有要设置的价格 慢速设置
                if aRealOrder<LeftCount: #目标在左侧总数内
                    Result=(RigthCount+LeftCount-aRealOrder)*StepVal;
                else:
                    if RigthCount>0:
                        Result=RigthCount*StepVal;  #
                    else:
                        Result=StepVal; # 右侧没有排名 这样很少
        else:  # 表明目标排名要排在右边
            if StepVal>0: #表明设置价格。
                if aRealOrder<(20+RigthCount):# aRealOrder 排在 21--28之间
                    Result=(20+RigthCount-aRealOrder)*StepVal;
                else:
                    Result=-1000 # 最低展现价格;
    else:   #当前排前大于零
        if StepVal==0: #表明要快速调价
            StepVal=GetAveSetPrice(ActivePrice,LastSetPrice,aActiveOrder,LastOrder,LeftCount,RigthCount);
            
        if aActiveOrder>aRealOrder: # 表明要向上调
            if aActiveOrder<20: # 表明已在左侧
                Result=(aActiveOrder-aRealOrder)*StepVal;  # StepVal 可以自动设置
            else:# 表明已在右侧
                if aRealOrder<20:#表明目标在左侧
                    Result=(aActiveOrder-20+LeftCount-aRealOrder)*StepVal;
                else:
                    Result=(aActiveOrder-aRealOrder)*StepVal;
        else:#表明想向下调
            if aActiveOrder<20: # 表明已在左侧
                if aRealOrder<20: # 要求目标在左侧
                    Result=(aActiveOrder-aRealOrder)*StepVal; #为负值
                else: # 要求目标在右侧
                    Result=-(aRealOrder-20+LeftCount-aActiveOrder)*StepVal;
            else:#表明已在右侧了
                Result=(aActiveOrder-aRealOrder)*StepVal; # 负值
                
    if Result!=0 and Result!=-1000 and LastOrder!=0 and LastSetPrice!=0 and aActiveOrder!=0:
        if abs(Result)>abs(LastSetPrice): #调价幅度大于上次
            if HasInArea(aRealOrder,LastOrder,aActiveOrder)==True: #是否这区间
                if LastOrder< aActiveOrder: #降的幅度过大
                    if aActiveOrder<20:  #所有排名都在左侧
                        TempResult=float(aActiveOrder-aRealOrder)/(aActiveOrder-LastOrder)*abs(LastSetPrice);
                    else: #当前排名在右侧 
                        if LeftCount>aRealOrder: #目标排名在左侧 
                            TempResult=float(aActiveOrder-20+LeftCount-aRealOrder)/(aActiveOrder-20+LeftCount-LastOrder)*abs(LastSetPrice);
                        else: #目标排名在右侧 
                            if LastOrder<20: #目标排名在右侧 上次排名在左侧 当前排名在右侧
                                TempResult=float(aActiveOrder-aRealOrder)/(aActiveOrder-20+LeftCount-LastOrder)*abs(LastSetPrice);
                            else: #目标排名在右侧 上次排名在右侧 当前排名在右侧
                                TempResult=float(aActiveOrder-aRealOrder)/(aActiveOrder-LastOrder)*abs(LastSetPrice);
                else: #升的幅度过大
                    if LastOrder<20: # 所有排名都在左侧
                        TempResult=float(aRealOrder-aActiveOrder)/(LastOrder-aActiveOrder)*abs(LastSetPrice);
                    else:
                        if LeftCount>aRealOrder: # 目标排名在左侧 当前排名在左侧 上次排名在左侧
                            TempResult=float(aRealOrder-aActiveOrder)/(LeftCount+LastOrder-20)*abs(LastSetPrice);
                        else:   # 目标排名在 右侧 上次排名在右侧
                            if aActiveOrder<20: #当前排名在右侧 目标排名在右侧
                                TempResult=float(LeftCount-aActiveOrder+aRealOrder-20)/(LeftCount-aActiveOrder+LastOrder-20)*abs(LastSetPrice);
                            else: #所有排名都在右侧
                                TempResult=float(aRealOrder-aActiveOrder)/(LastOrder-aActiveOrder)*abs(LastSetPrice);
                                
                if abs(Result)<=abs(TempResult):
                    TempResult=abs(Result)*0.8;
                    
                if Result>0:
                    Result=TempResult;
                else:
                    Result=-TempResult;
    #print 'result';
    #print Result;
    if Result<0.01 and Result>0:
        Result=0.01;
    if Result>-0.01 and Result<0:
        Result=-0.01;

    Result=float(int(Result*100))/100;
    return Result;
    
class BaiduGeter:#百度竞价排名获取类
    FPageCount=0;#总共个数
    ForderInt=0;#第几个排名    
    FLeftList=[];#右侧sem 词
    FRigthList=[];#右侧sem 词
    FKeyStr='';
    FHostUrl='';
    result=0;
    def __init__(self,aKeyStr,aHostUrl, aCookie):
        self.FKeyStr=aKeyStr;
        self.FHostUrl=aHostUrl;
        self.aCookie=aCookie;
        self.sCookie = Cookie.SimpleCookie(aCookie)
        #self.BaiduId = self.sCookie['__cas__id__3'].value
        self.sim = SimBrowser(self.sCookie)
        if self.GetToken() == -1:
            self.token=self.sCookie['__cas__st__3'].value
    def GetFixRank(self): # 获取竞价排名        
        tempList=[];
        self.FLeftList=[];
        self.FRigthList=[];
        self.FPageCount=0;
        
        #headers={'Content-Type':'application/x-www-form-urlencoded'};
        #refer='http://fengchao.baidu.com/nirvana/main.html?userid=3000534' + self.BaiduId
        refer = ''
        headers={'Cookie':self.aCookie,'Content-Type':'application/x-www-form-urlencoded','Refer':refer};

        #geturl='http://www.baidu.com';
        #res, content = self.sim.request(geturl,'GET',headers=headers);
        #headers={'Content-Type':'application/x-www-form-urlencoded'};
        geturl='http://www.baidu.com/s?wd='+ self.FKeyStr; #urlencode
        #geturl='http://fengchao.baidu.com/nirvana/request.ajax'; #urlencode
        #body={'path':'GET/Preview','userid':self.BaiduId,'token':self.token,
        #      'params':'{"keyword":"' + self.FKeyStr + '","area":1,"pageNo":0,"device":1}'};
        body = {}
        res, content = self.sim.request(geturl, 'POST', body=urlencode(body), headers=headers);
        #print content   
        #content=content.decode('GBK').encode('UTF-8');
        url_title_dict = dict()
        self.ForderInt = -1;
        pattern = r"<font size=\"3\" style=\"text-decoration:underline;\">(.*)<font size=\"-1\" color=\"#008000\" style=\"margin-left:6px;\">([^<]+)</font>"
        i = 0
        for title, target_url in re.findall(pattern, content):
            i = i + 1
            if self.ForderInt == -1 and target_url.lower().find(self.FHostUrl.lower()) != -1:
                self.ForderInt = i
            url_title_dict[target_url] = re.sub(r"<[^>]+>", "", title)
            
        self.FLeftList = [url_title_dict[url] + '\t' + url for url in url_title_dict]
        
        pattern_title = r"请您在www.baidu.com中搜索并查看'\)\"  ><font size=\"3\">(.*)</font></a><br>"
        pattern_url = r"<font size=\"-1\" color=\"#008000\">([^<]+)</font></a>"
        i = 20
        for title, target_url in zip(re.findall(pattern_title, content), re.findall(pattern_url, content)):
            i = i + 1
            if self.ForderInt == -1 and target_url.lower().find(self.FHostUrl.lower()) != -1:
                self.ForderInt = i
            url_title_dict[target_url] = re.sub(r"<[^>]+>", "", title)
            
        self.FRigthList = [url_title_dict[url] + '\t' + url for title in url_title_dict]

        self.FPageCount=len(self.FLeftList)+len(self.FRigthList);
        
    def GetToken(self): #获取Token
            refer='http://fengchao.baidu.com/nirvana/main.html?userid='+self.BaiduId;

            headers={'Cookie':self.aCookie,'Content-Type':'application/x-www-form-urlencoded','Referer':refer};
            body={'path':'GET/auth','userid':self.BaiduId,'token':'','params':'{"items":["username","token","servertime","ulevelid","optid","optname","optulevelid","spaceNewCount"]}'};
            posturl='http://fengchao.baidu.com/nirvana/request.ajax';
            res, content = self.sim.request(posturl,'POST',body=urlencode(body), headers=headers);
            if content.find('token"')>0:
                self.token=gethtmltagval(content,'token":"','','"');
                return 0;
            else:
                return -1;
    #Question on this function: Rank on the right side, start from 21;
    def GetCompeteOrder(self,CompeteUrl,Position):#获取竞争对手的排名 先进行关键词的获取 position boolean True 为压制 False 为跟随
        i=0;
        Result=0;
        lineStr='';
        for line in self.FLeftList:
            i=i+1;
            lineStr=str(line);
            CompeteUrl=CompeteUrl.encode("UTF-8");
            if lineStr.lower().find(CompeteUrl.lower())>0:#表明为该排名
                Result=i;
                break

        if Result == 0:
            i = 0
            for line in self.FRigthList:
                i=i+1;            
                lineStr=str(line);
                #lineStr=str(line).decode("UTF-8").encode("UTF-8");
                CompeteUrl=CompeteUrl.encode("UTF-8");
            
                if lineStr.lower().find(CompeteUrl.lower())>0:
                    Result=20+i;
        if Position: # 表明要压制
            if Result==1:#表明已是第一
                return 1;
            elif Result==0: #表明竞争对手没有出现
                return -1;
            elif Result==21: #表明要排在左键
                return len(self.FLeftList);
            else:
                return Result-1; #要提升一名
        else:
            if Result==self.FPageCount:#表明已是最后一位
                return self.FPageCount; #最低展现 
            elif Result==0: #表明竞争对手没有出现
                return -1;
            elif Result==len(self.FLeftList):# 表明已在左侧最下面
                return 21;
            else:
                return  Result+1; # 要降低一名
            
        return 0; #表明未查询到
    def GetSetPrice(self,aSetOrder,aStepVal,LastOrder,ActivePrice,LastSetPrice,MaxPrice,MinFee,KeyState): # 获取 需要调价 'price +'\t'+ 价格
        # aSetOrder 调价目标 aStepVal 调价幅度 0 为快速 0.1为稳定调价
        # LastOrder 上次排名 ActivePrice 当前出价 LastSetPrice 上次调价幅度 MaxPrice 最高上价 MinPrice 最低出价
        # MinFee 最低展示价格
        # 返回的结果 结果 0价格出价低，1成功 2偏高 3.已达最高价4.该词后台暂停 5.余额不足 6 出价低于展示价        
        NewStepVal=0;# 新的调价幅度
        aActiveOrder=int(self.ForderInt);
        #aActiveOrder = 3    #workaround for test
        LeftCount=len(self.FLeftList);
        RigthCount=len(self.FRigthList);
        if LeftCount==0 and RigthCount==0:
            self.result=6; # 不能展现
            return "0";
        if aSetOrder==11:   #排名在 左1~3 
            if aActiveOrder>=1 and aActiveOrder<=3: # 
                self.result=1;
                return "0";
        if aSetOrder==12:  #排名在 左4~6 
            if aActiveOrder>=4 and aActiveOrder<=6:
                self.result=1;
                return "0";
        if aSetOrder==aActiveOrder: #成功
            self.result=1;            
            return "0";
        else:
            if aSetOrder<20:
                if LeftCount==0: # 左侧没有排名
                    if aActiveOrder==21:
                        self.result=1;
                        return "0" # 已调最优
                        
                if aSetOrder>LeftCount:
                    if aActiveOrder==LeftCount:# 左侧最低端表明成功
                        self.result=1;
                        return "0";        
        NewPrice=0; #需要调的新价格   
        if KeyState==0:#该词状态正常 #workaround for test
            if float(LastSetPrice)==float(MaxPrice) and aSetOrder<aActiveOrder:
                self.result=3;
                return '0';
            
            NewStepVal=GetAdjustPrice(int(aSetOrder),aActiveOrder,float(ActivePrice),int(LastOrder),float(LastSetPrice),float(aStepVal),LeftCount,RigthCount);
            print 'NewStepVal %s' % NewStepVal
            if NewStepVal==-1000:#最低展现价。
                NewPrice=MinFee;
                NewStepVal=NewPrice-ActivePrice;
                self.result=0; 
            else:
                NewStepVal=float(int(NewStepVal*100))/100;
                if NewStepVal==0:
                    self.result=1;
                    return "0";
                
            NewPrice=ActivePrice+NewStepVal;
            NewPrice=float(int(NewPrice*100))/100; #新价格
            if NewPrice>=MaxPrice: #已达最高价
                NewPrice=MaxPrice;
                NewStepVal=NewPrice-ActivePrice;
                self.result=3; # 已达最高价
            else:
                if aActiveOrder==0:
                    self.result=0;
                    #return "0"; #未展现
                if NewPrice<MinFee: #调价低于最低价
                    NewPrice=MinFee;
                    NewStepVal=NewPrice-ActivePrice;
                    
            if NewPrice!=ActivePrice:
                if NewPrice-ActivePrice>0:
                    self.result=0; # 出价低
                else:
                    self.result=2; # 出价高
                return 'price'+'\t'+ str(NewPrice);
                # 需要调价
            else:
                if NewPrice==MaxPrice:
                    self.result=3; # 已达最高价
        elif KeyState==-2: # 未展现，应出最高价格
            self.result=0;
            if MaxPrice>=MinFee:
                NewPrice=MinFee;
            else:
                NewPrice=MaxPrice;
            return 'price'+'\t'+ str(NewPrice);            
        return '0';  
        
def main():
    #aCookie = 'BAIDUID=8309CD02C7606A38423E208C7637B5F5:FG=1; BDREFER=%7Burl%3A%22http%3A//news.baidu.com/%22%2Cword%3A%22%22%7D; BAIDU_WISE_UID=bens_1304218813_723; SFSSID=c5ab2b86eaa02999d55a876b88c8b8ff; H_BDCLCKID_SF=tJkH_D0yJIvHHP-k5-t_-P4DqxbXq-LJHmTZ_xK55U5DJRTdX5OZLjFJe-7JqxcJ3e0j0-OobUOasRRGMpDhXjtP3H-8-TJZfJueV-35b5rDjCDxDKTjhPrM5N7t0xTuMTb-VpF2a-J1qtjsXPc1X687WRuOB5OM-K78ahobX-JZ8xFz3hOoBPAwDPCE5bj2qRu8VI0b3f; BDUT=ik2r8309CD02C7606A38423E208C7637B5F5138dbfaa9b32; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a00954692266; __cas__st__3=8db90c9296026cecc1ea1d2dfd365d2b7896bf16894d24bf3e5a5725e759e5f4f6fa5fee552316fade8b96e0; __cas__id__3=3749026; __cas__rn__=95469226; JSESSIONID=6E2941F87E12C81737D53626F6ED6B0E; SAMPLING_COOKIE=e19a0f20dda4b3749026'
    aCookie = ''
    sender=BaiduGeter('优惠券团购','51BI.com', aCookie);
    sender.GetFixRank();
    print sender.ForderInt;    
    print sender.FPageCount;
    print len(sender.FLeftList);
    print len(sender.FRigthList);
    #print sender.GetCompeteOrder('tcxhlp.com',False);
    #aSetOrder,aActiveOrder,ActivePrice,LastOrder,LastSetPrice,StepVal,LeftCount,RigthCount;
    ##aSetOrder   lastOrder 上次排名  LastSetPrice 上次调价 StepVal 调价幅度 leftCount 左侧当前竞价个数 rigthCount 右侧当前竞价个数
    #print GetAdjustPrice(2,4,0.84,1,1.5,0,len(sender.FLeftList),len(sender.FRigthList));
    # aSetOrder,aStepVal,LastOrder,ActivePrice,LastSetPrice,MaxPrice,MinFee,KeyState
    #print sender.GetSetPrice(2,0,1,1.5,1.5,0.5,0.5,0);
    
    #print sender.GetSetPrice(2, 0.0, 5, 1.5, 1.5, 0.3, 0.5, 0);
    print sender.GetCompeteOrder('51bi.com',False);
    
    #print GetSetPrice(3 0.1 15 1.5 1.5 1.5 0.5 0);
    
    #ActivePrice,LastSetPrice,aActiveOrder,LastOrder,LeftCount,RigthCount

    #print GetAveSetPrice(3,1,22,3,10,8);
    

    
if __name__ == "__main__":
    main();        
        
        
        
