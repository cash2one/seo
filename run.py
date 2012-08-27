# -*-coding:utf-8 -*-

import threading
import time
import BaiduRank
import GetCompany
import GetSuggestion
import GetDiagnose
import sqliteconn

class thread_company(threading.Thread):
    ''''''
    def __init__(self, sqlconn_, interval=60*10):
        threading.Thread.__init__(self, name = 'crawler_company')
        self.interval = interval
        self.sqlconn = sqlconn_

    def run(self):
        while True:
            GetCompany.thread_crawler_company(self.sqlconn)
            print 'I\'m sleeping...'
            time.sleep(self.interval)
            print 'Working again...'

class thread_word_sug(threading.Thread):
    ''''''
    def __init__(self, sqlconn_, interval=60*10):
        threading.Thread.__init__(self, name = 'crawler_sug')
        self.interval = interval
        self.sqlconn = sqlconn_

    def run(self):
        while True:
            #PrBdkey.thread_sug()
            GetSuggestion.thread_sug(self.sqlconn)
            print 'I\'m sleeping...'
            time.sleep(self.interval)
            print 'Working again...'

class thread_rank(threading.Thread):
    ''''''
    def __init__(self, sqlconn_, interval=60*10):
        threading.Thread.__init__(self, name = 'crawler_rank')
        self.interval = interval
        self.sqlconn = sqlconn_

    def run(self):
        while True:
            BaiduRank.thread_rank(self.sqlconn)
            print 'I\'m sleeping...'
            time.sleep(self.interval)
            print 'Working again...'


class thread_query(threading.Thread):
    ''''''
    def __init__(self, sqlconn_, interval=60*10):
        threading.Thread.__init__(self, name = 'crawler_query')
        self.interval = interval
        self.sqlconn = sqlconn_

    def run(self):
        while True:
            #BaiduRank.thread_query()
            GetSuggestion.thread_query(self.sqlconn)
            print 'I\'m sleeping...'
            time.sleep(self.interval)
            print 'Working again...'

class thread_diagnose(threading.Thread):
    ''''''
    def __init__(self, sqlconn_, interval=60*10):
        threading.Thread.__init__(self, name = 'crawler_diagnose')
        self.interval = interval
        self.sqlconn = sqlconn_
        print 'im not ok...'

    def run(self):
        while True:
            GetDiagnose.thread_diagnose(self.sqlconn)
            print 'I\'m sleeping...'
            time.sleep(self.interval)
            print 'Working again...'

def main(sqlconn):
    #sqlconn = sqliteconn.sqlconn()
    crawler_company = thread_company(sqlconn_=sqlconn, interval=1000)
    #crawler_query = thread_query(sqlconn_=sqlconn)
    crawler_rank = thread_rank(sqlconn_=sqlconn)
    #crawler_sug = thread_word_sug(sqlconn_=sqlconn)
    #crawler_diagnose = thread_diagnose(sqlconn_=sqlconn)
    
    #crawler_company.start()    
    #crawler_query.start()
    crawler_rank.start()
    #crawler_sug.start()
    #crawler_diagnose.start()

    #crawler_query.join()
    #crawler_rank.join()
    #crawler_company.join()
    #crawler_sug.join()
    print 'thread working behind...'

if __name__ == '__main__':
    main('company.db')
    print 'main thread exit...'
