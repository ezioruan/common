#! /usr/bin/env python
# coding=utf-8
'''
Created on 2013-04-09
@todo:游戏服务器邮件通知(包括coreserver和gameserver)
@author: xianwei
'''
import reporter 
from twisted.internet.threads import deferToThread
import config

__server_reporter = None

class Server_Report(reporter.Email_Reporter):
    def __init__(self):
        super(Server_Report, self).__init__(config.smtp_host, config.sender_mail, config.sender_psw)
        self.bind(config.mail_info_file, config.subsciber_info_file)
        
def send_mail(mail_id, extend_info = ''):
    '''
            发送邮件
    '''
    global __server_reporter
    
    if not __server_reporter:
        __server_reporter = Server_Report()
    deferToThread(__server_reporter.send_report, mail_id, extend_info)

def game_server_twisted_log_send_mail(msg):
    '''
    :param msg:
    '''
    send_mail(config.GAME_SERVER_TWISTED_ERROR_LOG_MAIL_ID, msg)
    
def game_server_error_send_mail(msg, *args):
    '''
    :param msg:
    '''
    send_mail(config.GAME_SERVER_ERROR_MAIL_ID, msg%args)
    
def game_server_fatal_send_mail(msg, *args):
    '''
    :param msg:
    '''
    send_mail(config.GAME_SERVER_FATAL_MAIL_ID, msg%args)
    
def core_server_twisted_log_send_mail(msg):
    '''
    coreservice报错发邮件
    :param msg:
    '''
    send_mail(config.CORE_SERVER_TWISTED_ERROR_LOG_MAIL_ID, msg)
