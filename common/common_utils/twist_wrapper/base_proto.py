#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2012-7-8

@author: adaws
'''
from twisted.internet.protocol import Protocol
import struct
import time
import timeit
from twisted_log import ProtocolLog
from twisted.internet.reactor import callLater
from common.common_utils.twist_wrapper.multiPack_pb2 import MultiPacks
from common.common_utils.twist_wrapper import common_setting

##factory should own method permit and deal
class BaseProtocol(Protocol, ProtocolLog):
    delay = 0
    def connectionMade(self):
        self.connect_can_made = False
        peer = self.transport.getPeer()
        if not self.factory.permit(host=peer.host):
            self.INFO("%s, host is (%s)"%(self.factory.peer_checker.rule(), peer.host))
            self.transport.loseConnection()
            return

        self.INFO("%s Connetected at %s"%(peer.host, time.time()))
        self.status = 0
        self.connect_can_made = True
        self.set_crypt_ins(None, None)
        self.deal_tick_dct = {}
        self.access_tick_dct = {}
        self.need_send_msg_lst = []
        
    def connectionLost(self, reason):
        Protocol.connectionLost(self, reason)
        
    def dataReceived(self, data):

            
        if len(data) < 2:return
        
        header = struct.unpack_from('h', data[:2])[0]
        deal_res = self.factory.deal(self, header, data[2:])

        if common_setting.__DEBUG__:
            self.factory.DEBUG('DataReceived == Data(%s)  Len(%s) Result(%s)=='%(data, len(data), deal_res))
        
    def encrypt(self, data):
        if self.encoder != None:
            data = self.encoder.encode(data) 
        return data

    def decrypt(self, data):
        if self.decoder != None:
            data = self.decoder.decode(data)
        return data
   
    def set_crypt_ins(self, encoder=None, decoder=None):
        self.encoder = encoder
        self.decoder = decoder

    def send(self, protobuf_ins):
        already_have_message = self.need_send_msg_lst != []
        header, message_str = self.factory.get_message_info(protobuf_ins)
        self.need_send_msg_lst.append((header, message_str))
        
        if common_setting.__DEBUG__:
            self.factory.DEBUG('send Header(%s)  Message(%s) Already_have_message(%s)'%(header, message_str, already_have_message))
        
        if not already_have_message:
            callLater(self.delay, self.delay_send)
    
    def delay_send(self):
        message_cnt = len(self.need_send_msg_lst)
        
        if common_setting.__DEBUG__:
            self.factory.DEBUG("delay_send delay(%s) message_cnt(%s)"%(self.delay, message_cnt))
            
        if message_cnt == 0:return
        elif message_cnt == 1:
            header, message_str = self.need_send_msg_lst[0]
            total_msg = struct.pack('h', header) + self.encrypt(message_str)
            self.transport.write(total_msg)
            self.need_send_msg_lst = []
            return
        
        pack_ins = MultiPacks()
        for header, mesage in self.need_send_msg_lst:
            single = pack_ins.packs.add()
            single.header, single.data = header, mesage
        
        message_str = pack_ins.SerializeToString()
        total_msg = struct.pack('h', 0) + self.encrypt(message_str)
        self.transport.write(total_msg)
        self.need_send_msg_lst = []
    
    def get_status(self):return self.status
    def set_status(self, status):
        self.status = status

    