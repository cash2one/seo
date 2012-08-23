#!/usr/bin/python
# -*-coding:utf-8 -*-
import sqlite3;
import datetime;
import sys
import os
import codecs
import hashlib;
import base64
import time

def read_group_info(table_name):
    sql = ('select * from ' + table_name)
    
    dbpath = 'company.db'
    try:
        conn = sqlite3.connect(dbpath)
    except:
        print 'Connect db error!'
        return []

    try:
        #print query
        cur = conn.cursor()
        cur.execute(sql)
        print 'query ok...'
        ret = cur.fetchall()
        return ret
    except:
        print 'query error...'
        return []


def query_sql(dic, company):
    sql = ('select * from ' + company + ' where ' +
           '"groupid" = "' + dic[0] +
           '" and "keyword" = "' + dic[1] +
           '" and "company_name" = "' + dic[3] +
           '" and "telephone" = "' + dic[6] + '"')
    return sql
 
def gen_sql_str(dic, table_name):
    ret = 'insert into ' + table_name + ' values('
    date = time.localtime(time.time())
    date = time.strftime('%Y-%m-%d %H-%M-%S', date)
    dic.append(date)
    for i in xrange(0, len(dic)):
        ret += '"' + dic[i] + '"'
        if i != len(dic) - 1:
            ret += ','
        else:
            ret += ')'
    #print ret
    return ret

def insert_multi(dic, table):
    dbpath = 'company.db'
    try:
        conn = sqlite3.connect(dbpath)
    except:
        print 'Connect db error!'
        return
    
    sql = (gen_sql_str(dic, table))
    #print sql
    try:
        conn.execute(sql);
        conn.commit();
        print 'insert ok...';
    except:
        print 'insert error...'
        conn.close();
        return
    conn.close()    

def insert(dic, table):
    dbpath = 'company.db'
    try:
        conn = sqlite3.connect(dbpath)
    except:
        print 'Connect db error!'
        return
    query = query_sql(dic, table)
    try:
        print query
        cur = conn.cursor()
        cur.execute(query)
        print 'query ok...'
        if len(cur.fetchall()) != 0:
            print 'Exist same company'
            return
    except:
        print 'query error...'
        return

    sql = (gen_sql_str(dic, table))
    #print sql
    try:
        print sql
        conn.execute(sql);
        conn.commit();
        print 'insert ok...';
    except:
        print 'insert error...'
        conn.close();
        return
    conn.close()

def main():
    dic =['as', '2','3','fad','5','adf','7','8','9']
    #insert(dic)
    #print time.time()
    print read_group_info('group_info_rank')

if __name__ == "__main__":
    main();

