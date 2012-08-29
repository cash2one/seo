# -*-coding:utf-8 -*-

import threading
import time
import BaiduRank
import GetCompany
import GetSuggestion
import GetDiagnose
import sqliteconn

lock_of_suggestion = threading.Lock()
lock_of_diagnose = threading.Lock()

class thread_company(threading.Thread):
    ''''''
    def __init__(self, sqlconn_, interval=60*5):
        threading.Thread.__init__(self, name = 'crawler_company')
        self.interval = interval
        self.sqlconn = sqlconn_

    def run(self):
        while True:
            GetCompany.thread_crawler_company(self.sqlconn)
            #print 'I\'m sleeping...'
            time.sleep(self.interval)
            #print 'Working again...'

class thread_word_sug(threading.Thread):
    ''''''
    def __init__(self, sqlconn_, interval=60*10):
        threading.Thread.__init__(self, name = 'crawler_sug')
        self.interval = interval
        self.sqlconn = sqlconn_

    def run(self):
        #while True:
            #PrBdkey.thread_sug()
        if lock_of_suggestion.acquire(100):
            GetSuggestion.thread_sug(self.sqlconn)
            lock_of_suggestion.release()
            #print 'I\'m sleeping...'

class thread_rank(threading.Thread):
    ''''''
    def __init__(self, sqlconn_, interval=60*5):
        threading.Thread.__init__(self, name = 'crawler_rank')
        self.interval = interval
        self.sqlconn = sqlconn_

    def run(self):
        while True:
            BaiduRank.thread_rank(self.sqlconn)
            #print 'I\'m sleeping...'
            time.sleep(self.interval)
            #print 'Working again...'

class thread_query(threading.Thread):
    ''''''
    def __init__(self, sqlconn_, interval=60*10):
        threading.Thread.__init__(self, name = 'crawler_query')
        self.interval = interval
        self.sqlconn = sqlconn_

    def run(self):
        if lock_of_suggestion.acquire(100):
            #print 'I\'m working...'
            GetSuggestion.thread_query(self.sqlconn)
            lock_of_suggestion.release()
            #print 'I\'m finishing working...'

class thread_diagnose(threading.Thread):
    ''''''
    def __init__(self, sqlconn_, interval=60*10):
        threading.Thread.__init__(self, name = 'crawler_diagnose')
        self.interval = interval
        self.sqlconn = sqlconn_
        #print 'im not ok...'

    def run(self):
        if lock_of_diagnose.acquire(100):
            GetDiagnose.thread_diagnose(self.sqlconn)
            lock_of_diagnose.release()
            #print 'I\'m sleeping...'

def main(sqlconn):
    #sqlconn = sqliteconn.sqlconn()
    crawler_company = thread_company(sqlconn_=sqlconn)
    #crawler_query = thread_query(sqlconn_=sqlconn)
    crawler_rank = thread_rank(sqlconn_=sqlconn)
    #crawler_rank_multi = thread_rank(sqlconn_=sqlconn)
    #crawler_sug = thread_word_sug(sqlconn_=sqlconn)
    #crawler_diagnose = thread_diagnose(sqlconn_=sqlconn)
    
    crawler_company.start()
    crawler_rank.start()
    
    #crawler_query.start()
    #crawler_rank_multi.start()
    #crawler_sug.start()
    #crawler_diagnose.start()
    #print 'thread working behind...'

if __name__ == '__main__':
    main('company.db')
    print 'main thread exit...'
