# -*-coding:utf-8 -*-
#! /bin/python

u'鲜花',u'鲜花'
tt = unicode('鲜花','utf-8')
print tt.encode('gbk')

a = '\xe4\xbd\xa0'
aa = unicode(a, 'utf-8')
print a.encode('gbk')
