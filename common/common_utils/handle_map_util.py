#! /usr/bin/env python
# coding=utf-8
'''
Created on 2012-7-18

@author: ezioruan

TestCode in common.common_utils.tests.test_handler_map.test.py
'''


from ctypes import *
from common.common_utils.table_reader import Record,TableData


class HandleMapConfig(Record):
    
    _fields_ = [
                ('header', c_int),                   # 封包头
                ('need_status', c_int),              # 需要的状态
                ('handler', c_char * 50),            # 处理对应封包头的函数
                ('protobuf_cls', c_char * 50),       # 收到的数据的实例类
                ('access_interval', c_float),          # 访问的间隔 单位s
                ('deal_interval', c_float),            # 处理的间隔 单位s
                ('info', c_int),                     # 描述   
               ]
    

def NotDefinedFunc(tag):
    def NotDefinedHandler(proto_ins, protobuf_ins, **kwargs):
        print '(%s) Not Defined (%s)Deal Message(%s) kwargs(%s)'%(tag, id(proto_ins), protobuf_ins, kwargs)
        return True
    
    return NotDefinedHandler



def get_handler_map(file_path, handler_module, protobuf_module):
    '''
    获得处理类的映射字典
    @param file_path:    映射表路径
    @param handler_module:    所有handler的模块
    @param protobuf_module:    所有protobuf类所在的的模块 
    '''
    reload(handler_module)
    reload(protobuf_module)
    data = TableData(file_path, HandleMapConfig, ['header'], 2)
    
    handle_map = {}
    for record in data.records:
        handler_func = handler_module.__dict__.get(record.handler, NotDefinedFunc(record.handler))
        protobuf_cls = protobuf_module.__dict__.get(record.protobuf_cls)
        data = record.need_status, handler_func, protobuf_cls, record.access_interval, record.deal_interval
        if handle_map.has_key(record.header):raise Exception('header repeated : %s'%record.header)
        handle_map[record.header] = data
    
    return handle_map


def get_proto_cls_map(file_path):
    '''
    
    @param file_path:    映射表路径
    '''
    data = TableData(file_path, HandleMapConfig, ['header'], 2)
    proto_cls_map = {}
    for record in data.records:
        proto_cls_map[record.protobuf_cls] = record.header
    
    return proto_cls_map
            
    

    