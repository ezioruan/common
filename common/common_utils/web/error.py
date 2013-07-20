#! /usr/bin/env python
# coding=utf-8
'''
Created on 2012-7-24

@author: ezioruan
'''
from twisted.web import http

def http404(request):
    request.setResponseCode(http.NOT_FOUND)
    request.write('<H1>404  YOU KNOW !<H1>')
    request.finish()
       
        
def http500(request,exception):
    request.setResponseCode(http.INTERNAL_SERVER_ERROR)
    request.write(str(exception))
    request.finish()


