#!/usr/bin/python
# coding=utf-8
'''
Created on 2013-1-29
生成CA证书
@author: GreatWall
'''
import sys
import os
import time
import math

DEF_PASS_DAYS = 365
#生成CA证书, pass_days为过期时间(单位天)，过期的话会调用shell命令重新生成
#此函数目前只针对linux
def Generate_CERT(shell_file, cert_file, logger = None, pass_days = DEF_PASS_DAYS):
    #windows下先不考虑，没有证书就去linux下生成然后拿回来就好了
    if sys.platform[:3] == 'win':
        if logger:
            logger.INFO("Server Start In Windows System! No Process!")
        return

    if not os.path.isfile(shell_file):
        if logger:
            logger.FATAL("Can't Find Shell File : %s"%shell_file)
        return
    
    #存在证书文件，检查是否过期，过期的话就重新生成一份
    if os.path.isfile(cert_file):
        ctime = os.path.getmtime(cert_file)
        now = time.time()
        #未过期，不处理
        if pass_days > math.floor((now - ctime)/(24*60*60)):
            if logger:
                logger.INFO("Cert File Not Out Of Date, No Process!")
            return
        else:
            if logger:
                logger.INFO("Cert File Out Of Date. Call Shell Generate.")
    else:
        if logger:
            logger.INFO("Not Exist Cert File:%s. Call Shell Generate."%cert_file)
    
    old_path = os.getcwd() #获取当前工作目录
    os.chdir(os.path.split(shell_file)[0])  #设置当前文件的目录为工作目录
    ret = os.system("sh %s"%shell_file)
    if 0 != ret:
        if logger:
            logger.FATAL("sh generate_ca failed!")
    os.chdir(old_path)  #还原旧的工作目录
   
if __name__ == "__main__":
    try: 
        import logger
        from control.conn_common import SERVER_CRT_PATH, KEY_AND_CRT_PATH
    except:
        class CLogger(object):
            def __init__(self):
                pass
            
            def INFO(self, msg):
                print "INFO    %s"%msg
            
            def FATAL(self, msg):
                print "FATAL    %s"%msg
        logger = CLogger()
        KEY_AND_CRT_PATH = os.path.dirname(__file__)
        SERVER_CRT_PATH = os.path.join(KEY_AND_CRT_PATH, "server.crt")
        
    Generate_CERT(os.path.join(KEY_AND_CRT_PATH, "generate_ca.sh"), SERVER_CRT_PATH, logger)
