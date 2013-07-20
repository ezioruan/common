#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2012-7-15

@author:  adaws
'''
[
DEAL_RESULT_SUCCESS,                #成功 
DEAL_RESULT_NONE,                   #没有相关头的处理函数
DEAL_STATUS_NEEDED,                 #需要状态
DEAL_ACCESS_TIME_INTERVAL,          #封包头访问间隔
DEAL_RESULT_TIME_INTERVAL,          #处理间隔 非法
DEAL_PARSE_ERROR,                   #解密错或序列化错
DEAL_RESULT_ERROR,                  #处理过程出错
] = xrange(7)
