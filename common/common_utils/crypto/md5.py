#! /usr/bin/env python
# coding=utf-8
'''
Created on 2012-9-11

@author: ezioruan
'''
from twisted.python.hashlib import md5

def get_md5_digest(code):
    m = md5()
    m.update(code)
    return m.hexdigest()
