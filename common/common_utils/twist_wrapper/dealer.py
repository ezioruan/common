#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2012-7-15

@author:  adaws
'''
from common.common_utils.twist_wrapper.defines import DEAL_RESULT_SUCCESS, DEAL_RESULT_NONE, DEAL_STATUS_NEEDED, DEAL_ACCESS_TIME_INTERVAL, DEAL_RESULT_TIME_INTERVAL, DEAL_PARSE_ERROR, DEAL_RESULT_ERROR
from common.common_utils.error_dump import format_exc
import timeit
from common.common_utils.twist_wrapper.multiPack_pb2 import MultiPacks
from common.common_utils.twist_wrapper import common_setting

class base_dealer(object):
    def __init__(self, *args, **kwargs):
        self.factory = kwargs.get('factory')
        self.handler_map = kwargs.get('handler_map', {})
        self.proto_map = kwargs.get('proto_map', {})
        
    def set_factory(self, factory):
        self.factory = factory
    
    def set_handler_map(self, handler_map):
        self.handler_map = handler_map
    
    def set_proto_map(self, proto_map):
        self.proto_map = proto_map

    def deal(self, *args, **kwargs):
        proto_ins, header, data = args[:3]
        
        is_subpack = kwargs.get('is_subpack', False)
        
        
        #不能子包中包含子包 没有必要
        if header == 0:
            if is_subpack:return DEAL_PARSE_ERROR
            
            msg_ins = MultiPacks()
            try:
                decrypt_data = proto_ins.decrypt(data)
                msg_ins.ParseFromString(decrypt_data)
            except:
                
                #这里加入__debug__ 根据python 启动的参数 python -O 会设置__debug__ false, -OO 会去除 docstrings
                if __debug__:
                    self.factory.DEBUG('Parse Data Error: \n %s\n%s'%(format_exc()))
                return DEAL_PARSE_ERROR
            
            kwargs['is_subpack'] = True
            
            result_lst = []
            for pack in msg_ins.packs:
                deal_res = self.deal(proto_ins, pack.header, pack.data, **kwargs) != DEAL_RESULT_SUCCESS
                result_lst.append((pack.header, deal_res))

                    
            return result_lst
        
        dealer_info = self.handler_map.get(header)
        
        if common_setting.__DEBUG__:
            self.factory.DEBUG('DealPack Header(%s) Data(%s), Dealer(%s)'%(header, data, dealer_info))
            
        if not dealer_info:return DEAL_RESULT_NONE
        need_status, handler, protobuf_cls, access_interval, deal_interval = dealer_info
        if need_status != None and need_status != proto_ins.get_status():return DEAL_STATUS_NEEDED
        
        cur_time = timeit.default_timer()
        if access_interval != 0:
            last_access_tick = proto_ins.access_tick_dct.get(header)
            if last_access_tick != None:
                if cur_time - last_access_tick <= access_interval:return DEAL_ACCESS_TIME_INTERVAL
            
            proto_ins.access_tick_dct[header] = cur_time
        
        last_deal_tick = proto_ins.deal_tick_dct.get(header)
        if last_deal_tick != None:
            if cur_time - last_deal_tick < deal_interval:
                return DEAL_RESULT_TIME_INTERVAL
            
        msg_ins = None
        if protobuf_cls != None:
            try:
                msg_ins = protobuf_cls()
                
                #子包外层解密过了 里层不解密
                if is_subpack:decrypt_data = data
                else:decrypt_data = proto_ins.decrypt(data)
                msg_ins.ParseFromString(decrypt_data)
            except:
                
                #这里加入__debug__ 根据python 启动的参数 python -O 会设置__debug__ false, -OO 会去除 docstrings
                if __debug__:
                    self.factory.ERROR('Parse Data Error: \n %s\n%s'%(format_exc()))
                return DEAL_PARSE_ERROR

        try:
            if handler(proto_ins, msg_ins):
                proto_ins.deal_tick_dct[header] = cur_time
        except SystemExit, e:
            if e.message == 0:
                self.factory.INFO('Normal Exit with code(0)')
                raise
            else:
                self.factory.ERROR('Error Exit with code(%d)'%e.message)
        
        except:
            error_msg, locals_msg = format_exc()
            self.factory.ERROR('Deal Data Error: \n %s\n%s\nheader(%s) dealer(%s) msg_ins(%s)'%(error_msg, locals_msg, header, handler, msg_ins))
            return DEAL_RESULT_ERROR
        
        return DEAL_RESULT_SUCCESS
    
    def get_message_info(self, protobuf_ins):
        return self.proto_map.get(protobuf_ins.__class__.__name__), protobuf_ins.SerializeToString()
    

