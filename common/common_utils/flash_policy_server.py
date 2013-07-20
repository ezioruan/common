#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2012-7-11

@author:  adaws
'''

from twisted.internet.protocol import Factory, Protocol
from twisted.internet.reactor import run, listenTCP
policy_file = '''\
<?xml version="1.0"?>
<cross-domain-policy>
   <allow-access-from domain="*" to-ports="*" />
</cross-domain-policy>
'''

#policy 是否起作用测试方法 linux输入下面的命令 看输出内容 是否和policy_file内容一致
#  python -c 'print "<policy-file-request/>%c" % 0' | nc 192.168.1.222 843



class PolicyProtocol(Protocol):
    def connectionMade(self):pass
    
    def dataReceived(self, data):
        if data.strip()[:22] != "<policy-file-request/>":return
        self.transport.write(policy_file)
        self.transport.loseConnection()
        
class PolicyFactory(Factory):
    def __init__(self):pass
    
    
def policy_server(port=843):
    try:
        policy_factory = PolicyFactory()
        policy_factory.protocol = PolicyProtocol
        listenTCP(port, policy_factory)
    except Exception, e:
        print 'Start policy Server at port(%s) failed!'%port
        print 'reason: %s', e

    
if __name__ == '__main__':
    policy_server()
    print 'RunPolicy'
    run()
    