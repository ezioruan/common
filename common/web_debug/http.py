#! /usr/bin/env python
# coding=utf-8
'''
Created on 2012-7-23

@author: ezioruan
'''
from common.common_utils.web.http import listen, listenSSL
from common.web_debug import debug_setting


def listen_debug_web_site(port,log_path,log_tag,url_map,static_server_url=None):
    listen(port, log_path, log_tag, url_map, 
           debug_setting.STATIC_DIR, debug_setting.TEMPLATE_DIR,static_server_url)

    

def listen_debug_web_site_ssl(port, log_path, log_tag, url_map, server_key_path, server_crt_path,static_server_url=None):
    listenSSL(port, log_path, log_tag, url_map, 
           debug_setting.STATIC_DIR, debug_setting.TEMPLATE_DIR, server_key_path, server_crt_path,static_server_url)

