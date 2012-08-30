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
    '''得到百度着陆页'''
    host = 'http://www.baidu.com/s'
    url = host + '?wd=site%3A' + target_url + '+' + key_word
    re, content = sim.request(url, 'GET')
    content = content.decode('utf-8')
    ret = base.FindSection(content, '<span class="g">', '</span>')
    if len(ret) == 0:
        return 'unfind'
    if ret[0].find(' ') == -1:
        return 'unfind'
    # 去除可能出来的<br></br>标签
    return clean_tag(ret[0].lstrip().split(' ')[0])

def get_relate(key_word):
    sim = SimHttp.SimBrowser('')
    url = host_name + '?relate=' + key_word
    re, content = sim.request(url, 'GET')
    content = content.decode('utf-8')
    return content.split('\n')[:-1]

def get_flow(key_word):
    url = host_name + '?keyword=' + key_word
    re, content = SimHttp.SimBrowser('').request(url, 'GET')
    baidu_google = content[:-1].split('\t')[:-1]
    # 加入百度收录量
    ranker_bd = BaiduRank.GetBaiduRank()
    baidu_collect = ranker_bd.GetBaiduNum(key_word)
    baidu_google.append(baidu_collect)
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
            ret = [word]
            ret.extend(get_flow(word))
            yield ret

def get_query_of_sug_word(groupid, url, sqlconn):
    suggestion = sqlconn.select_table(groupid, 'suggestion')
    if len(suggestion) == 0:
        return
    for row_sug in suggestion:
        sug_word = row_sug[2]
        rank_getter = BaiduRank.GetBaiduRank()
        my_rank, my_rank_url = rank_getter.GetBaiduNatureRank(sug_word, url)
        ret_dic = {'rank':my_rank,
                   'load_url':get_baidu_loadurl(sug_word, url)}
        s_dic = {'groupid':groupid,
                 'sug_word':sug_word}
        sqlconn.update_table(ret_dic, s_dic, 'suggestion')

def get_query_of_group(group, sqlconn):
    groupid = str(group[0])
    status = group[5]
    #print status,
    # 如果推荐词抓取未完成, 返回
    if status != 3:
        return False

    # 更改状态为关键字推荐进行中
    ret_dic = {'status':'4'}
    s_dic = {'groupid':str(group[0])}
    sqlconn.update_table(ret_dic, s_dic, 'group_info_sug')

    url = group[4]
    if url == None:
        return False
    get_query_of_sug_word(groupid, url, sqlconn)

    # 更改状态为推荐词查询完成
    ret_dic = {'status':'5'}
    s_dic = {'groupid':str(group[0])}
    sqlconn.update_table(ret_dic, s_dic, 'group_info_sug')
    return True

def get_sug_of_group(group, sqlconn):
    # 关键字状态为初始
    if group[5] != 0:
        return False

    # 更改状态为关键字推荐进行中
    ret_dic = {'status':'1'}
    s_dic = {'groupid':str(group[0])}
    sqlconn.update_table(ret_dic, s_dic, 'group_info_sug')

    key_words = group[2].split('#')
    forbid_words = group[3].split('#')
    for key_word in key_words:
        for sug_res in get_suggestion(key_word, forbid_words):
            ist_ret = [str(group[0]), key_word]
            ist_ret.extend(sug_res)
            ist_ret.extend(['-1','unknown'])
            sqlconn.insert_multi(ist_ret, 'suggestion')

    # 更改状态为关键字推荐完成
    ret_dic = {'status':'2'}
    s_dic = {'groupid':str(group[0])}
    sqlconn.update_table(ret_dic, s_dic, 'group_info_sug')
    return True

def thread_query(sqlconn_name):
    sqlconn = sqliteconn.sqlconn(sqlconn_name)
    group_ret = sqlconn.read_group_info('group_info_sug')
    idx = 0
    for group in group_ret:
        if get_query_of_group(group, sqlconn):
            time.sleep(10)

def thread_sug(sqlconn_name):
    sqlconn = sqliteconn.sqlconn(sqlconn_name)
    group_ret = sqlconn.read_group_info('group_info_sug')
    for group in group_ret:
        get_sug_of_group(group, sqlconn)
        time.sleep(10)


    
def main():
    thread_query('company.db')

if __name__ == '__main__':
    main()
