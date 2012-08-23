# -*-coding:utf-8 -*-
# write jizhongkui
import httplib2
import random;
import urllib;
import sys;
import os;
import socket
import HTMLParser
import sqliteconn

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
        #cookiestr = '; '.join(self.cookie.output(attrs=[], header="").split('\r\n'));
        cookiestr = ''
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

def GetRandUserAgent():
    random_num=int(random.random()*10);
    UserAgent='Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)';
    if random_num==1:
       UserAgent='Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)';
    if random_num==2:
        UserAgent='Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 2.0.50727)';
    if random_num==3:
        UserAgent='Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; SLCC1)';
    if random_num==4:
        UserAgent='Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; WOW64; Trident/4.0)';
    if random_num==5:
        UserAgent='Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)';
    if random_num==6:
        UserAgent='Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0)';
    if random_num==7:
        UserAgent='Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10';
    if random_num>8:
        UserAgent='Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)';
    return UserAgent;

def GetBdSuggestion(key_word):
    cookie = ''
    sim = SimBrowser(cookie, GetRandUserAgent())
    #print key_word
    url = 'http://suggestion.baidu.com/su?wd=' + key_word.encode('utf-8')
    url += '&p=3&cb=window.bdsug.sug&sid=1288_1329_1266_1229_1343_1185_1282_1287_1320_1332_1367&t=1345470017747'
    url += '&p=3&cb=window.bdsug.sug&sid=1288_1329_1266_1229_1343_1185_1282_1287_1320_1332_1367&t=0'
    head = {'Content-Type':'application/x-www-form-urlencoded',
            'Cookie':cookie,
            'Host':'suggestion.baidu.com',
            'Referer':'http://www.baidu.com/'}
    re, content = sim.request(url,'GET', headers=head)
    decode_content = content
    #decode_content = content.decode('gbk').encode('utf-8')
    #print type(decode_content)
    s = decode_content.find('[')
    e = decode_content.find(']')
    allwords = decode_content[s + 1:e]
    words = unicode(allwords, 'gbk').strip('"').split('"')
    ret = []
    for word in words:
        if word != u',':
            ret.append(word)
    return ret

class FindUrlParser(HTMLParser.HTMLParser):
    ''' '''
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.flag = False
        self.sug = []

    def handle_starttag(self, tag, attrs):
        HTMLParser.HTMLParser.handle_starttag(self, tag, attrs)
        if 'table' == tag:
            if len(attrs) == 1:
                self.flag = True
        if self.flag and 'a' == tag:
            for key,value in attrs:
                if key == 'href':
                    #print value
                    urlword = value.split('&')[0].split('=')[1]
                    self.sug.append(unicode(urllib.unquote(urlword.encode('utf-8')),'utf-8'))
                    #print unicode(urllib.unquote(urlword).decode('utf-8'))
        if 'div' == tag:
            self.flag = False

def find_key_div(html_src):
    s = html_src.find('<div id="rs">')
    if s == -1:
        return -1, ''
    e = html_src.find('</div>', s)

    #print s, e
    #print html_src[s:e+6]
    return html_src[s:e+6]

def ParserHtmlSug(html_src):
    htmlparser = FindUrlParser()
    htmlparser.feed(find_key_div(html_src))

    return htmlparser.sug
    
def GetHtmlSuggestion(key):
    attrs = {'ie':'utf-8', 'pn':'0'}
    url_attrs = urllib.urlencode(attrs)
    url_domain = 'http://www.baidu.com/s?'
    url = url_domain + url_attrs + '&wd='
    url += key.encode('utf-8')
    html_src = urllib.urlopen(url).read().decode('utf-8')

    return ParserHtmlSug(html_src)
            
def GetBdWords(akey):
    search_key = akey
    dic = GetBdSuggestion(search_key)
    html_sug = GetHtmlSuggestion(search_key)
    for item in html_sug:
        if item not in dic:
            dic.append(item)
    return dic

def cvt2unicode(key, need_word):
    try:
        u_key = unicode(key, 'utf-8')
    except:
        u_key = key

    try:
        u_need_word = unicode(need_word, 'utf-8')
    except:
        u_need_word = need_word

    return u_key, u_need_word

def GetSugWords(akey, need_word):
    start_key, u_need_word = cvt2unicode(akey, need_word)
    ret = [start_key]
    idx = 0
    while len(ret) < 50 and idx < len(ret):
        cur_key = ret[idx]
        #print cur_key, u_need_word
        dic = GetBdWords(cur_key)
        for item in dic:
            #print item, u_need_word.encode('utf-8')
            if item.find(u_need_word) != -1 and item not in ret:
                ret.append(item)
        idx += 1
    ret = ret[1:]
    #for item in ret:
    #    print item
    return ret

def get_sug_of_group(group):
    keys = group[2].split('#')
    forbiden = group[3].split('#')
    print len(forbiden[1])
    for key in keys:
        # 得到推荐词列表，每个词插入数据库一行
        sugs = GetSugWords(key, key)
        for sug in sugs:
            flag = True
            for it in forbiden:
                if len(it) > 0 and sug.find(it) != -1:
                    flag = False
                    break
            # 如果不在过滤词表中，添加进数据库
            if flag:
                ret = [str(group[0]), key, sug]
                ret.append('unknown baidu flow')
                ret.append('unknown google flow')
                ret.append('unknown estimate flow')
                sqliteconn.insert_multi(ret, 'suggestion')
            
def thread_sug():
    group_ret = sqliteconn.read_group_info('group_info_sug')
    for group in group_ret:
        get_sug_of_group(group)
    
def main():
#    adic=[];
#    aFilterdic=[];
    GetBdWords('xinhua')
#    GetSugWords(u'鲜花',u'鲜花')
#    import codecs
#    ainfo=codecs.encode( u"\r\n".join(adic),'utf-8');
#    saveinfo(ainfo,'all');
#    for key in adic:
#        if key.find(u'鲜花')>-1: # 过滤
#            aFilterdic.append(key);
#
#    ainfo=codecs.encode(u"\r\n".join(aFilterdic),'utf-8');        
#    saveinfo(ainfo,'filter');
    
if __name__ == "__main__":
    #main();
    thread_sug()
