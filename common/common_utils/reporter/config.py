#! /usr/bin/env python
# coding=utf-8
'''
Created on 2013-4-18

@author: Administrator
'''
import os

smtp_host = 'smtp.163.com'
sender_mail = 'youc_server@163.com'
sender_psw = 'www.youc.com?_12'
mail_info_file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))), "mail_info.txt")
subsciber_info_file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__))), "subsciber_info.txt")

#gameserver tiwsted报错的邮件通知的邮件id
GAME_SERVER_TWISTED_ERROR_LOG_MAIL_ID = 2

#gameserver logger error的邮件通知的邮件id
GAME_SERVER_ERROR_MAIL_ID = 3

#gameserver logger fatal的邮件通知的邮件id
GAME_SERVER_FATAL_MAIL_ID = 4

#coreserver twisted 报错的邮件通知id
CORE_SERVER_TWISTED_ERROR_LOG_MAIL_ID = 5