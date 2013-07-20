#! /usr/bin/ python
# -*- coding: utf-8 -*-
'''
Created on 2013-2-5
用于回报状态，到指定邮箱（邮箱可设置手机提醒）
@author: GreatWall
'''
import os
import timeit
import mail
from ctypes import * #@UnusedWildImport
from common.common_utils.table_reader import Record, TableData
import traceback
from common.common_utils.twist_wrapper import twisted_log

#邮件信息
class Mail_Info(Record):
    _fields_ = [
                ('mail_id', c_int),            #邮件
                ('subject', c_char * 100),
                ('info', c_char * 400),    #邮件正文信息
                ('limit_interval', c_int),   #限制的通知间隔
               ]

#订阅者信息
class Subsciber_Info(Record):
    _fields_ = [
                ('recver_mail', c_char * 100),     #接收者邮箱
                ('subscibe_list', c_char * 1000),           #订阅的邮件列表
               ]


class Oper_Info(object):
    def __init__(self):
        self.subject = ""                        #邮件主题
        self.info = "report info"             #邮件正文信息
        self.limit_interval = 60 * 1000  #时间间隔，在这个间隔内的不做处理
        self.last_tick = 0   #上一次处理的时间  
        self.recver_list = []      #接收者列表

#邮件报告
class Email_Reporter(object):
    def __init__(self, smtp_host, sender_mail, sender_psw):
        self.__smtp_host = smtp_host
        self.__sender_mail = sender_mail
        self.__sender_psw = sender_psw
        self.__mail_info_file = ""
        self.__subsciber_info_file = ""
        self.__mail_info_file_last_modify_time = 0  #消息文件的最后一次修改时间
        self.__subsciber_info_file_last_modify_time = 0  #接收者订阅文件最后一次修改时间
        self.__report_info_dict = {}         #消息报告字典{'id':report_info_obj, ....}
        self.__report_data = None
        self.__recver_data = None
        self.__errinfo = ""

    def bind(self, mail_info_file, subsciber_info_file):
        '''
        注：下面的举例均使用tab分割
        report_info_file : 定义了一堆用于报告消息的对应文件（每行的内容类似于：1(信息ID)    出错啦(具体的信息)    1234(通知间隔，在一定时间内只通知一次，单位毫秒)）
        recver_info_file： 记录了一堆接收者对应要接收的信息ID列表的文件(每行内容类似于:xieccheng@yahoo.com.cn(邮箱地址)    [1,2,3,4,5...])
        '''
        self.__mail_info_file = mail_info_file
        self.__subsciber_info_file = subsciber_info_file
        return self.__read_file()
        
    def __read_file(self):
        try:
            if not os.path.isfile(self.__mail_info_file):
                self.__errinfo = "Can't find this file：%s"%(self.__mail_info_file)
                return False
            
            if not os.path.isfile(self.__subsciber_info_file):
                self.__errinfo = "Can't find this file：%s"%(self.__subsciber_info_file)
                return False
            
            is_reset = False
            
            modify_time = os.path.getmtime(self.__mail_info_file)
            if modify_time != self.__mail_info_file_last_modify_time:
                self.__report_data = TableData(self.__mail_info_file, Mail_Info, ['mail_id'])
                self.__mail_info_file_last_modify_time = modify_time
                is_reset = True
                
            modify_time = os.path.getmtime(self.__subsciber_info_file)
            if modify_time != self.__subsciber_info_file_last_modify_time:
                self.__recver_data = TableData(self.__subsciber_info_file, Subsciber_Info, ['recver_mail'])
                self.__subsciber_info_file_last_modify_time = modify_time
                is_reset = True
            
            if not is_reset:
                return True
            
            self.__report_info_dict = dict()
            report_count = self.__report_data.get_count()
            for index in xrange(report_count):
                report_info = self.__report_data.get_record_by_index(index)
                mail_id = report_info.mail_id
                oper_info = Oper_Info()
                oper_info.subject = report_info.subject
                oper_info.info  = report_info.info
                oper_info.limit_interval = report_info.limit_interval
                self.__report_info_dict[mail_id] = oper_info
            
            recver_count = self.__recver_data.get_count()
            for index in xrange(recver_count):
                recver_info = self.__recver_data.get_record_by_index(index)
                recver_mail = recver_info.recver_mail                 #接收者邮箱
                subscibe_list = eval(recver_info.subscibe_list)             #订阅的报告ID列表
                for mail_id in subscibe_list:
                    oper_info = self.__report_info_dict.get(mail_id)
                    if not oper_info:
                        continue
                    if recver_mail in oper_info.recver_list:
                        continue
                    oper_info.recver_list.append(recver_mail)
        except:
            self.__errinfo = traceback.format_exc()
            return False
        return True

    def send_report(self, mail_id, extend_info = ""):
        '''
        info_id:要通知的消息的ID号
        extend_info:扩展消息，一般用于通知具体的信息，如（调用堆栈等）
        '''
        if not self.__read_file():
            return False
        
        oper_info = self.__report_info_dict.get(mail_id)
        if not oper_info:
            self.__errinfo = "Can't find oper_info from info_id:%s"%mail_id
            return False
        now_time = timeit.default_timer() * 1000
        if oper_info.last_tick == 0 or now_time - oper_info.last_tick >= oper_info.limit_interval:
            content = oper_info.info
            if extend_info:
                content += "\r\n" + "-----------------"*4
                content += "\r\n" + extend_info
            ret, ret_info = mail.send_mail(self.__smtp_host, self.__sender_mail, self.__sender_psw, 
                           oper_info.recver_list, oper_info.subject, content)
            oper_info.last_tick = now_time
            if not ret:
                self.__errinfo = ret_info
                twisted_log.INFO('send mail error! error_info = %s'%self.__errinfo)
                return False
        return True
                
    def get_errinfo(self):
        return self.__errinfo
            

__email_reporter = None
#初始化邮件回报者
#返回结果和信息:ret, info(ret为True时，info为空， 为False时，info为错误信息)
def init_email_reporter(smtp_host, sender_mail, sender_psw, mail_info_file, subsciber_info_file):
    global __email_reporter
    if __email_reporter is None:
        __email_reporter = Email_Reporter(smtp_host, sender_mail, sender_psw)
    return __email_reporter.bind(mail_info_file, subsciber_info_file), __email_reporter.get_errinfo()

def get_email_reporter(logger = None):
    global __email_reporter
    if __email_reporter is None:
        if logger:
            logger.WARN("__email_reporter is None, Please call init_email_reporter first!")
            return None
    return __email_reporter

#--------------------------------------------------------------------------------------------------------------
def test():
    import time
    cur_dir = os.path.dirname(__file__)
    mail_info_file = os.path.join(cur_dir, "mail_info.txt")
    subsciber_info_file = os.path.join(cur_dir, "subsciber_info.txt")
    smtp_server = "smtp.163.com" 
    sender = "youc_server@163.com" 
    psw = "www.youc.com?_12"
    ret, ret_info = init_email_reporter(smtp_server, sender, psw, mail_info_file, subsciber_info_file)
    if not ret:
        print ret_info
        return
    start_time = time.time()
    while True:
        ret = get_email_reporter().send_report(1, "这是一个扩展信息，你接看看")
        if not ret:
            print "err:",get_email_reporter().get_errinfo()
            return
#        print "send mail ok"
        time.sleep(1)
        if time.time() - start_time >= 120:
            break
    print "test finish"
if __name__ == '__main__':
    test()