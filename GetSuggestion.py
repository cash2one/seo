# -*-coding:utf-8 -*-

import SimHttp
import BaiduRank
import Cookie
import sqliteconn

host_name = 'http://keys.tu1001.com:1110'

def clean_tag(src):
    ret = src
    while True:
        s = ret.find('<')
        if s == -1:
            return ret
        e = ret.find('>')
        ret = ret[:s] + ret[e+1:]
    return ret

def get_baidu_loadurl(key_word, target_url):
    host = 'http://www.baidu.com/s'
    url = host + '?wd=site%3A' + target_url + '+' + key_word
    print url
    cookie = Cookie.SimpleCookie()
    sim = SimHttp.SimBrowser(cookie)
    re, content = sim.request(url, 'GET')
    content = content.decode('utf-8')
    ret = BaiduRank.FindSection(content, '<span class="g">', '</span>')
    #for item in ret:
    #    print item.split(' ')[1]
    #print ret
    if len(ret) == 0:
        return 'unfind'
    if ret[0].find(' ') == -1:
        return 'unfind'
    # 去除可能出来的<br></br>标签
    return clean_tag(ret[0].split(' ')[1])

def get_relate(key_word):
    sim = SimHttp.SimBrowser('')
    #url = host_name + '?keyword=' + key_word
    url = host_name + '?relate=' + key_word
    print url
    re, content = sim.request(url, 'GET')
    content = content.decode('utf-8')
    return content.split('\n')[:-1]

def get_flow(key_word):
    url = host_name + '?keyword=' + key_word
    re, content = SimHttp.SimBrowser('').request(url, 'GET')
    return content[:-1].split('\t')

def get_suggestion(start_key, forbidden):
    sug_word = get_relate(start_key)
    for word in sug_word:
        flag = True
        for item in forbidden:
            if len(item) > 0 and word.find(item) != -1:
                flag = False
                break
        if flag:
            #print word.encode('gbk')
            #get_flow(word)
            ret = [word]
            ret.extend(get_flow(word))
            yield ret

def get_query_of_sug_word(groupid, url, sqlconn):
    #sug_word = group[2]
    #s_dic = {'groupid':str(group[0]),
    #         'sug_word':sug_word}
    #update_dic = {'rank':BaiduRank.}
    suggestion = sqlconn.select_table(groupid, 'suggestion')
    if len(suggestion) == 0:
        return
    for row_sug in suggestion:
        sug_word = row_sug[2]
        print url, sug_word
        my_rank, my_rank_url = BaiduRank.GetBaiduPageFull(sug_word, url)
        #print my_rank, my_rank_url
        ret_dic = {'rank':my_rank,
                   'load_url':get_baidu_loadurl(sug_word, url)}
        s_dic = {'groupid':groupid,
                 'sug_word':sug_word}
        for item in ret_dic:
            print item, ret_dic[item]
        sqlconn.update_table(ret_dic, s_dic, 'suggestion')

def get_query_of_group(group, sqlconn):
    groupid = str(group[0])
    status = group[5]
    # 如果推荐词抓取未完成, 返回
    if status != 1:
        return

    url = group[4]
    if url == None:
        return
    get_query_of_sug_word(groupid, url, sqlconn)

    # 更改状态为推荐词查询完成
    ret_dic = {'status':'2'}
    s_dic = {'groupid':str(group[0])}
    sqlconn.update_table(ret_dic, s_dic, 'group_info_sug')

def get_sug_of_group(group, sqlconn):
    # 关键字状态为促初始
    if group[5] != 0:
        return

    key_words = group[2].split('#')
    #if group[3] != '':
    forbid_words = group[3].split('#')
    for key_word in key_words:
        for sug_res in get_suggestion(key_word, forbid_words):
            ist_ret = [str(group[0]), key_word]
            ist_ret.extend(sug_res)
            ist_ret.extend(['-1','unknown'])

            sqlconn.insert_multi(ist_ret, 'suggestion')
            #for item in sug_res:
                #print item

    # 更新状态为抓取推荐词完成
    ret_dic = {'status':'1'}
    s_dic = {'groupid':str(group[0])}
    sqlconn.update_table(ret_dic, s_dic, 'group_info_sug')

def thread_query(sqlconn_name):
    sqlconn = sqliteconn.sqlconn(sqlconn_name)
    group_ret = sqlconn.read_group_info('group_info_sug')
    print len(group_ret)
    idx = 0
    for group in group_ret:
        get_query_of_group(group, sqlconn)
        print '#####################'
    print 'Finish>>>>>>>>>>>>>>'

def thread_sug(sqlconn_name):
    sqlconn = sqliteconn.sqlconn(sqlconn_name)
    group_ret = sqlconn.read_group_info('group_info_sug')
    for group in group_ret:
        get_sug_of_group(group, sqlconn)
    
def main():
    #get_suggestion(u'笔记本',[])
    #thread_sug()
    thread_query()
    #print get_baidu_loadurl(u'鲜花', 'caihhua.com')

if __name__ == '__main__':
    main()
