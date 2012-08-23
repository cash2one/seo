#!/usr/bin/python
# -*-coding:utf-8 -*-
import sys;
import os;
import urllib2;
import httplib2;
import Cookie;
import re
import socket;

class SimBrowser:
    """
      封装的httplib2 的包.
    """
    socket.setdefaulttimeout(15); # 超时限制 15秒
    UserAgent="";
    cookie=None;
    httplink = httplib2.Http();    
    httplink.follow_redirects = False;
    hostname="";    
    def __init__(self, cookie, UserAgent="Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)"):
        self.cookie = cookie;
        self.UserAgent = UserAgent;        
        
    def gen_cookie_str(self):
        try:
            cookiestr = '; '.join(self.cookie.output(attrs=[], header="").split('\r\n'));
            if len(cookiestr) <= 0:
                return "";
            else:
                return cookiestr;
        except:
            return "";

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
                newheaders = self.prepare_request_header(newheaders); # 此处为更新当前的cookie
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
        
def main():
    pass;
if __name__ == "__main__":
    main();

