# -*-coding:utf-8 -*-

import SimHttp
import BaiduRank
import Cookie
import sqliteconn
import time
import Base

cookie = Cookie.SimpleCookie()
sim = SimHttp.SimBrowser(cookie)
base = Base.Base()

#class Suggestion():
#    '''get suggestions of keyword'''
#    def __init__(self)

host_name = 'http://keys.tu1001.com:1110'

def clean_tag(src):
    ret = src
    #print ret
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
    
    re, content = sim.request(url, 'GET')
    content = content.decode('utf-8')
    #print content
    ret = base.FindSection(content, '<span class="g">', '</span>')
    #for item in ret:
    #    print item.split(' ')[1]
    #print ret[0]
    if len(ret) == 0:
        return 'unfind'
    if ret[0].find(' ') == -1:
        return 'unfind'
    # 去除可能出来的<br></br>标签
    #print ret[0].lstrip().split(' ')
    return clean_tag(ret[0].lstrip().split(' ')[0])

def get_relate(key_word):
    sim = SimHttp.SimBrowser('')
    #url = host_name + '?keyword=' + key_word
    url = host_name + '?relate=' + key_word
    print url
    re, content = sim.request(url, 'GET')
    #print 'load url ok...'
    #print content
    content = content.decode('utf-8')
    return content.split('\n')[:-1]

def get_flow(key_word):
    url = host_name + '?keyword=' + key_word
    re, content = SimHttp.SimBrowser('').request(url, 'GET')
    #return content[:-1].split('\t')
    baidu_google = content[:-1].split('\t')[:-1]
    ranker_bd = BaiduRank.GetBaiduRank()
    baidu_collect = ranker_bd.GetBaiduNum(key_word)
    baidu_google.append(baidu_collect)
    #time.sleep(1)
    return baidu_google

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
    suggestion = sqlconn.select_table(groupid, 'suggestion')
    if len(suggestion) == 0:
        return
    for row_sug in suggestion:
        sug_word = row_sug[2]
        print url, sug_word
        rank_getter = BaiduRank.GetBaiduRank()
        my_rank, my_rank_url = rank_getter.GetBaiduNatureRank(sug_word, url)
        #my_rank, my_rank_url = BaiduRank.GetBaiduPageFull(sug_word, url)
        #my_rank = 0
        #my_rank_url = '...'
        #print my_rank, my_rank_url
        ret_dic = {'rank':my_rank,
                   'load_url':get_baidu_loadurl(sug_word, url)}
        s_dic = {'groupid':groupid,
                 'sug_word':sug_word}
        for item in ret_dic:
            print item, ret_dic[item]
        sqlconn.update_table(ret_dic, s_dic, 'suggestion')
        #time.sleep(5)

def get_query_of_group(group, sqlconn):
    groupid = str(group[0])
    status = group[5]
    print status,
    # 如果推荐词抓取未完成, 返回
    if status != 3:
        return False

    # 更改状态为关键字推荐进行中
    ret_dic = {'status':'4'}
    s_dic = {'groupid':str(group[0])}
    sqlconn.update_table(ret_dic, s_dic, 'group_info_sug')

    url = group[4]
    print url
    if url == None:
        return False
    #print url
    get_query_of_sug_word(groupid, url, sqlconn)

    # 更改状态为推荐词查询完成
    ret_dic = {'status':'5'}
    s_dic = {'groupid':str(group[0])}
    sqlconn.update_table(ret_dic, s_dic, 'group_info_sug')
    return True

def get_sug_of_group(group, sqlconn):
    # 关键字状态为初始
    if group[5] != 0:
        return

    # 更改状态为关键字推荐进行中
    ret_dic = {'status':'1'}
    s_dic = {'groupid':str(group[0])}
    sqlconn.update_table(ret_dic, s_dic, 'group_info_sug')

    key_words = group[2].split('#')
    #if group[3] != '':
    forbid_words = group[3].split('#')
    for key_word in key_words:
        #print key_word
        for sug_res in get_suggestion(key_word, forbid_words):
            ist_ret = [str(group[0]), key_word]
            ist_ret.extend(sug_res)
            ist_ret.extend(['-1','unknown'])
            print ist_ret
            sqlconn.insert_multi(ist_ret, 'suggestion')
            #for item in sug_res:
                #print item
    # 更改状态为关键字推荐完成
    ret_dic = {'status':'2'}
    s_dic = {'groupid':str(group[0])}
    sqlconn.update_table(ret_dic, s_dic, 'group_info_sug')
    return True

def thread_query(sqlconn_name):
    sqlconn = sqliteconn.sqlconn(sqlconn_name)
    group_ret = sqlconn.read_group_info('group_info_sug')
    print len(group_ret)
    idx = 0
    for group in group_ret:
        if get_query_of_group(group, sqlconn):
            time.sleep(10)
        print '#####################'
    print 'Finish>>>>>>>>>>>>>>'

def thread_sug(sqlconn_name):
    sqlconn = sqliteconn.sqlconn(sqlconn_name)
    group_ret = sqlconn.read_group_info('group_info_sug')
    for group in group_ret:
        get_sug_of_group(group, sqlconn)
        print 'sleep for crawler next group of sug...'
        time.sleep(10)


    
def main():
    #get_suggestion(u'笔记本',[])
    #thread_sug('company.db')
    thread_query('company.db')
    #print get_baidu_loadurl(u'鲜花', 'caihhua.com')

if __name__ == '__main__':
    main()
