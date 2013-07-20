#! /usr/bin/env python
# coding=utf-8
'''
Created on 2012-9-6

@author: ezioruan
'''
import sys
import base64
from common.common_utils.error_dump import format_exc
from twisted.web import http
from common.common_utils.twist_wrapper import twisted_log
from common.common_utils import chromelogger

class DebugStream(object):
    data = ''
    back_stdout = None
    back_stderr = None
    def __init__(self):pass
    def flush(self):pass
    def write(self, *args):
        try:
            self.data += ''.join([str(i) for i in args])
        except:
            pass
        
    def writelines(self, *args):
        try:
            self.data += str([(str(i) + '\n') for i in args])
        except:
            pass
        
    def __str__(self):return 'Null_Out'
    def fileno(self):return - 1
    def fetch(self):
        tmp = DebugStream.data
        DebugStream.data = ''
        if twisted_log.log_inited:
            twisted_log.DEBUG('web debug fetch --> %s' % tmp)
        return tmp
        
    def enable(self):
        DebugStream.back_stdout = sys.stdout
        DebugStream.back_stderr = sys.stderr
        
        sys.stdout = DebugStream
        sys.stderr = DebugStream
        
    def disable(self):
        if DebugStream.back_stdout != None:
            sys.stdout = DebugStream.back_stdout
        
        if DebugStream.back_stderr != None:
            sys.stderr = DebugStream.back_stderr

    
    flush = classmethod(flush)
    write = classmethod(write)
    writelines = classmethod(writelines)
    __str__ = classmethod(__str__)
    fileno = classmethod(fileno)
    fetch = classmethod(fetch)
    enable = classmethod(enable)
    disable = classmethod(disable)
    

def require_session(func, *args, **kwargs):
    def _vatify_login(*args, **kwargs):
        request = args[0]
        session = request.getSession()
        
        if not request.sessions.get(session.uid):
            request.write('Session Timeout,Please login again!')
            request.setResponseCode(http.OK)
            request.finish()        
        else:
            return func(*args, **kwargs)
    
    return _vatify_login


def print2response(func, *args, **kwargs):
    def _run_with_debug_stream(*args, **kwargs):
        request = args[0]
        DebugStream.enable()
        if twisted_log.log_inited:
            twisted_log.DEBUG('debug %s with args(%s)' % (func.__name__,request.args))
        func(*args, **kwargs)
        DebugStream.disable()
        response_data = DebugStream.fetch()
        #add chrome log
        header = chromelogger.get_header()
        if header is not None:
            request.setHeader(header[0],header[1])
        request.write(response_data)
        request.setResponseCode(http.OK)
        request.finish()        
    
    return _run_with_debug_stream



@require_session
@print2response
def debug_with_session(request):
    return __debug(request)

    
@print2response
def debug(request):
    return __debug(request)
    
def __debug(request):
    b64_str = request.get_args('codeSource')
    code_source = base64.b64decode(b64_str)
    try:
        code = compile(code_source, '<string>', 'exec')
        eval(code)
    except:
        error_info, local_msg = format_exc()
        print '\n\n  ====Frames====%s'%error_info
        print  '\n  ====Locals====%s'%local_msg
        


    