#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2012-7-15

@author:  adaws
'''

class PeerChecker(object):
    def permit(self, *args, **kwargs):assert "This method(permit) should be implemeneted"
    def rule(self):assert "This method(rule) should be implemeneted"
    
    
class NoCheck(PeerChecker):
    def permit(self, *args, **kwargs):return True
    def rule(self):return 'All Will Pass'
    
class WhiteListCheck(PeerChecker):
    def __init__(self, white_lst):
        if not type(white_lst) is set:
            self.white_set = set(white_lst)
        else:
            self.white_set = white_lst
    
    def permit(self, *args, **kwargs):
        host = kwargs.get('host')
        #print host, host in self.white_set
        return host in self.white_set
    
    def add_white(self, host):
        self.white_set.add(host)
    
    def del_white(self, host):
        if host in self.white_set:self.white_set.remove(host)
        
    def rule(self):return 'Host Should In(%s)'%self.white_set