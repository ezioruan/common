#! /usr/bin/env python
# coding=utf-8
'''
Created on 2012-6-18

@author: adaws
'''
import os
import time

DEFAULT_SUGGEST_POOL_SIZE = 200
class OsNotSupported(BaseException):
    '''Operate System is not supported
    '''
    pass

print 'System Platform is %s' % os.name
print 'Reactor Setup During...'

installed_tp = ''
if os.name == 'nt':
    installed_tp = 'Windows...'
    from twisted.internet import iocpreactor
    
    iocpreactor.install()

elif os.name == 'posix':
    installed_tp = 'Posix...'
    from twisted.internet import epollreactor
    epollreactor.install()

else:
    raise OsNotSupported, "Only support nt and posix Operate System"


from twisted.internet import reactor
reactor.suggestThreadPoolSize(DEFAULT_SUGGEST_POOL_SIZE)
print 'Reactor Setup Finished...Type(%s) Set suggestThreadPoolSize(%s)'%(installed_tp, DEFAULT_SUGGEST_POOL_SIZE)

