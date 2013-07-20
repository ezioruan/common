#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2012-7-15

@author:  adaws
'''

import os, time
import sys
import logging
from twisted.python.logfile import DailyLogFile
from twisted.python import threadable, log
from macpath import dirname


#@warning: DailyLogFile file buff_size=1 this may affect program performance 
class EveryDayLogFile(DailyLogFile):
    def shouldRotate(self):
        """Rotate when the date has changed since last write"""
        return self.toDate() != self.lastDate

    def _openFile(self):
        self.fix_path()
        DailyLogFile._openFile(self)

    def fix_path(self):
        file_name = '%04d-%02d-%02d' % (self.toDate())
        self.path = os.path.join(self.directory, "%s-%s" % (self.name, file_name))

    def rotate(self):
        if not (os.access(self.directory, os.W_OK)):return
        next_date = self.toDate(os.stat(self.path)[8])
        print 'Close Old LogFile(%s) ' % self.path
        self._file.close()
        self._openFile()
        self.lastDate = next_date
        print 'Open  New LogFile(%s)' % self.path
        
threadable.synchronize(EveryDayLogFile)

SERVER_NOTE = logging.FATAL + 10

log_inited = False
_log = None

_stdout = sys.stdout
_stderr = sys.stderr

AFTER_LOG_OPER = None
LOG_TAG = None

def init_log_path(dir_name, name_pre):
    global log_inited
    global _log
    
    assert not log_inited, 'Cannot init_log_path twice or more'
    log.FileLogObserver.timeFormat = "%H:%M:%S"
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
    fileObj = EveryDayLogFile.fromFullPath(os.path.join(dir_name, name_pre))
    log.startLogging(fileObj, setStdout=0)
    log_inited = True
    
    _log = get_log()
    
def get_log(log_tag=''):
    def _logf(msg, level):

        if level < _log_level:return
        if level >= SERVER_NOTE:
            _stdout.write("%s %s %s\n" %("%04d-%02d-%02d %02d:%02d:%02d"%time.localtime()[:6], "[NOTE]%s"%log_tag, msg))

        log.msg("%s%s" %(log_tag,  msg), system=logging._levelNames.get(level, 'NOTE'))

    return _logf


#每个不同的服务器有自己的lOG路径 这里是公用模块 每个要用的服务器需要自己 初始化LOG路径 

_log_level = logging.NOTSET


def set_log_level(lv):
    global _log_level
    _log_level = lv
    

def NOTE(msg):_log(msg, SERVER_NOTE)
def FATAL(msg):
    _log(msg, logging.FATAL)
    if AFTER_LOG_OPER:
        AFTER_LOG_OPER('[%s]\n%s'%(LOG_TAG, msg))
def ERROR(msg):
    _log(msg, logging.ERROR)
    if AFTER_LOG_OPER:
        AFTER_LOG_OPER('[%s]\n%s'%(LOG_TAG, msg))
        
def WARN(msg):_log(msg, logging.WARN)
def INFO(msg):_log(msg, logging.INFO)
def DEBUG(msg):_log(msg, logging.DEBUG)

class ProtocolLog(object):
    def NOTE(self, msg):self.factory.NOTE(msg)
    def FATAL(self, msg):self.factory.FATAL(msg)
    def ERROR(self, msg):self.factory.ERROR(msg)
    def WARN(self, msg):self.factory.INFO(msg)
    def INFO(self, msg):self.factory.INFO(msg)
    def DEBUG(self, msg):self.factory.DEBUG(msg)

class FactoryLog(object):
    def __init__(self, *args, **kwargs):
        self._log = get_log(kwargs.get('LogTag', ''))
        
    def NOTE(self, msg):self._log(msg, SERVER_NOTE)
    def FATAL(self, msg):self._log(msg, logging.FATAL)
    def ERROR(self, msg):self._log(msg, logging.ERROR)
    def WARN(self, msg):self._log(msg, logging.WARN)
    def INFO(self, msg):self._log(msg, logging.INFO)
    def DEBUG(self, msg):self._log(msg, logging.DEBUG)
    
