#!/usr/bin/python
# -*-coding:utf-8 -*-

#
# 封装数据库操作。所有的更新和插入操作都必须检查锁
# 
# 比较简单的封装策略，
# 插入的时候没有考虑关键字对应，直接按顺序将传入的序列中每个
# 值都依次插入到数据库表中。
# 更新的时候需要传入2个字典， 分别对应更新项和查询项。
#
#


import sqlite3;
import datetime;
import sys
import os
import codecs
import hashlib;
import base64
import time
import threading

dbpath = 'company.db'
lock_of_sql = threading.Lock()

class sqlconn():
    def __init__(self, dbname):
        self.dbname = dbname
        try:
            self.conn = sqlite3.connect(self.dbname)
        except:
            print 'Connect db error!'
        #pass

    def select_table(self, groupid, table_name):
        sql = 'select * from ' + table_name + ' where "groupid" = ' + groupid + ''

        try:
            print sql
            cur = self.conn.cursor()
            cur.execute(sql)
            ret = cur.fetchall()
            return ret
        except:
            print 'query error...'
            return []

    def update_table(self, ist_dic, s_dic, table_name):
        sql = 'update ' + table_name + ' set'
        for item in ist_dic:
            sql += ' "' + item + '" = "' + ist_dic[item] + '",'
        sql = sql[:-1]
        sql += ' where'
        for item in s_dic:
            sql += ' "' + item + '" = "' + s_dic[item] + '" and'
        sql = sql[:-4]
        
        try:
            #print sql
            if lock_of_sql.acquire():
                self.conn.execute(sql);
                self.conn.commit();
                lock_of_sql.release()
            #print 'insert ok...';
        except:
            print 'insert error...'
            return
        #print sql
     
    def read_group_info(self, table_name):
        sql = ('select * from ' + table_name + ' order by groupid desc')

        try:
            #print sql
            cur = self.conn.cursor()
            cur.execute(sql)
            #print 'query ok...'
            ret = cur.fetchall()
            return ret
        except:
            print 'query error...'
            return []


    def query_sql(self, dic, company):
        sql = ('select * from ' + company + ' where ' +
               '"groupid" = "' + dic[0] +
               '" and "keyword" = "' + dic[1] +
               '" and "last_update" = "' + dic[2] +
               '" and "company_name" = "' + dic[3] +
               '" and "telephone" = "' + dic[6] + '"')
        return sql
     
    def gen_sql_str(self, dic, table_name):
        ret = 'insert into ' + table_name + ' values('
        date = time.localtime(time.time())
        date = time.strftime('%Y-%m-%d %H:%M:%S', date)
        dic.append(date)
        try:
            for i in xrange(0, len(dic)):
                #print dic[i].encode('utf-8')
                if len(dic[i].strip()) != 0:
                    ret += '"' + dic[i] + '"'
                else:
                    ret += '" "'
                if i != len(dic) - 1:
                    ret += ','
                else:
                    ret += ')'
        except:
            ret = ''
            print 'generate sql str error!...'
        #print ret
        return ret

    def insert_multi(self, dic, table):
        sql = (self.gen_sql_str(dic, table))
        #print sql
        try:
            #print sql
            if lock_of_sql.acquire():
                self.conn.execute(sql)
                self.conn.commit()
                lock_of_sql.release()
            #print 'insert ok...';
        except:
            print 'insert error...'
            return

    def insert(self, dic, table):
        query = self.query_sql(dic, table)
        try:
            #print query
            cur = self.conn.cursor()
            cur.execute(query)
            #print 'query ok...'
            if len(cur.fetchall()) != 0:
                print 'Exist same company'
                return
        except:
            print 'query error...'
            return

        sql = (self.gen_sql_str(dic, table))
        #print sql
        try:
            #print sql
            if lock_of_sql.acquire():
                self.conn.execute(sql)
                self.conn.commit()
                lock_of_sql.release()
            #print 'insert ok...';
        except:
            print 'insert error...'
            return

def main():
    dic =['as', '2','3','fad','5','adf','7','8','9']
    conn = sqlconn('company.db')

if __name__ == "__main__":
    main();

