#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2012-7-15

@author:  adaws
'''
from common.common_utils.twist_wrapper.twisted_log import FactoryLog

class BaseFactory(FactoryLog):
    def __init__(self, *args, **kwargs):
        FactoryLog.__init__(self, *args, **kwargs)
        self.peer_checker = kwargs.get('peer_checker')
        self.dealer_ins = kwargs.get('dealer_ins')
        
    def set_peer_checker(self, peer_checker):
        self.peer_checker = peer_checker
    
    
    def permit(self, *args, **kwargs):
        if not self.peer_checker:return True
        return self.peer_checker.permit(*args, **kwargs)
        
    def set_dealer_ins(self, dealer_ins):
        self.dealer_ins = dealer_ins
        dealer_ins.set_factory(self)
    
    def deal(self, *args, **kwargs):
        assert self.dealer_ins != None, 'Must have a dealer'
        return self.dealer_ins.deal(*args, **kwargs)
    
    def get_message_info(self, proto_ins):
        return self.dealer_ins.get_message_info(proto_ins)

