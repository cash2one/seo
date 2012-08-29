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
        #sql = 'select * from ' + table_name

        try:
            print sql
            cur = self.conn.cursor()
            cur.execute(sql)
            #print 'query ok...'
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
    #insert(dic)
    #print time.time()
    #print read_group_info('group_info_rank')

if __name__ == "__main__":
    main();

