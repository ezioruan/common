#! /usr/bin/env python
# coding=utf-8
'''
Created on 2013-2-2

@author: adaws
'''
import smtplib 
from email.mime.text import MIMEText 
 


# 发送邮件函数 
#host : smtp服务器，发送者使用
#user : 
def send_mail(host, sender, psw, recver_list, subject, content): 
    '''''
    host : smtp服务器，发送者使用
    sender : 发送者邮箱账号
    psw : 发送者邮箱密码
    recver_list: 发送给谁
    subject: 主题
    content: 内容
    send_mail("smtp.163.com", "sender", "psw", ["xxx@126.com"], "sub", "context")
    ''' 
    msg = MIMEText(content, 'plain', 'utf-8') 
    msg['Subject'] = subject 
    msg['From'] = sender 
    msg['To'] = ";".join(recver_list) 
    try: 
        send_smtp = smtplib.SMTP()
        send_smtp.connect(host) 
        send_smtp.login(sender, psw) 
        send_smtp.sendmail(sender, recver_list, msg.as_string()) 
        send_smtp.close() 
    except Exception, e: 
        return False, str(e)
    
    return True, 'OK'


if __name__ == '__main__': 
    import time
    start = time.time()
    # 接收列表
    recver_list=['xcc@behill.com']
    
    # 设置服务器名称、用户名、密码以及邮件后缀 
    smtp_server = "smtp.163.com" 
    sender = "youc_server@163.com" 
    psw = "www.youc.com?_12"
    subject = "hello"
    content = "This is a test mail from Jiange Project!"
    
    ret, info = send_mail(smtp_server, sender, psw, recver_list, subject, content)
    if (ret): 
        print ("测试成功") 
    else: 
        print ("测试失败") 
    print time.time()-start