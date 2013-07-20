#! /usr/bin/env python
# coding=utf-8
'''
Created on 2012-9-4

@author: ezioruan
'''
from twisted.web import http
from twisted.web.server import Request, Site
from twisted.internet import reactor, threads, tcp

from error import http404,http500
from common.common_utils.twist_wrapper.twisted_log import FactoryLog, ProtocolLog
import os
from common.common_utils.web.template import TemplateManager
import mimetypes
import ujson
from twisted.internet import ssl
from common.common_utils.error_dump import format_exc
from common.web_debug import debug_setting
import time
import email.utils



def parse_date(ims):
    """ Parse rfc1123, rfc850 and asctime timestamps and return UTC epoch. """
    try:
        ts = email.utils.parsedate_tz(ims)
        return time.mktime(ts[:8] + (0,)) - (ts[9] or 0) - time.timezone
    except (TypeError, ValueError, IndexError, OverflowError):
        return None

class BaseRequestFactory(Request):
    
    site = Site(None)
    #sitepath is just to generate cookie
    sitepath = [os.path.dirname(__file__)]
    
    sessions = {}
    
    def process(self):
        if self.path.startswith('/static/'):
            static_server_url = self.channel.factory.static_server_url
            if static_server_url:
                self.redirect('%s%s' % (static_server_url,self.path))
                self.finish()
                return
            else:
                return self.get_static_resource()
        
        if self.path == r'/favicon.ico':
            threads.deferToThread(self.write_file, 'img/favicon.ico', self.channel.factory.static_file_dir)
            return
        
        print '--------> ', self.path
        url_handle_func = self.channel.factory.url_map.get(self.path)
        if url_handle_func:
            try:
                url_handle_func(self)
            except:
                error_info = '500 Error: \n %s\n%s'%(format_exc())
                self.log_info(error_info)
                http500(self, error_info)
        else:
            http404(self)
            
    def log_info(self,info):
        self.channel.INFO(info)
        
    
    def get_static_resource(self):
        file_name = self.path[len('/static/'):]
        static_dir = self.channel.factory.static_file_dir
        return self.write_file(file_name, static_dir)
        
    def write_file(self,file_name,file_dir):
        file_path = os.path.abspath(os.path.join(file_dir, file_name.strip('/\\')))
        if not os.path.isfile(file_path):
            http404(self)
            return
        header = dict()
        mimetype, encoding = mimetypes.guess_type(file_path)
        if mimetype: 
            header['Content-Type'] = mimetype
        if encoding: 
            header['Content-Encoding'] = encoding
        stats = os.stat(file_path)
        header['Content-Length'] = stats.st_size
        lm = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(stats.st_mtime))
        header['Last-Modified'] = lm
    
        ims = self.getHeader('if-modified-since')
        if ims:
            ims = parse_date(ims.split(";")[0].strip())
        if ims and int(ims) >= int(stats.st_mtime):
            header['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
            self.set_header(header)
            self.setResponseCode(http.NOT_MODIFIED)
            self.finish()
        else:
            self.setResponseCode(http.OK)
            self.set_header(header)
            with open(file_path, 'rb') as f:
                context = f.read()
                self.write(context)
            self.finish()

    def set_header(self,header):
        for key,value in header.iteritems():
            self.setHeader(key, value)
        
    def get_args(self,arg_name):
        return self.args.get(arg_name,[''])[0]
    
    def get_template_mgr(self):
        return self.channel.factory.template_mgr
    
    def render_and_response(self,template_name,var_dict={}):
        templdate_mgr = self.get_template_mgr()
        context = templdate_mgr.render(template_name, var_dict)
        self.write(context)
        self.setResponseCode(http.OK)
        self.finish()
        
    
    def render_debug_page(self):
        templdate_mgr = TemplateManager(debug_setting.TEMPLATE_DIR)
        html = templdate_mgr.render('debug.html')
        self.write(html)
        self.setResponseCode(http.OK)
        self.finish()
        
    
    
        
    def response_msg(self,msg,url=None):
        self.setResponseCode(http.OK)
        if url:
            render_dict = {'msg':msg,'url':url}
        else:
            render_dict = {'msg':msg,'url':self.path}
        self.render_and_response('auto_refresh.html', render_dict)
        
    def render_json(self,data):
        self.setResponseCode(http.OK)
        self.setHeader('Content-Type','application/json')
        self.setHeader('Content-Encoding','utf-8')
        self.write(ujson.dumps(data))
        self.finish()
        return
  
   
    
    
    
  


class BaseHttpChannel(http.HTTPChannel,ProtocolLog):
    requestFactory = BaseRequestFactory
    


class BaseHttpFactory(http.HTTPFactory,FactoryLog):

    protocol = BaseHttpChannel
    
    def __init__(self,log_path,log_tag,url_map,static_file_dir,template_dir,static_server_url=None):
        http.HTTPFactory.__init__(self, log_path)
        FactoryLog.__init__(self, LogTag=log_tag)
        self.url_map = url_map
        self.static_file_dir = static_file_dir
        self.template_mgr = TemplateManager(template_dir)
        self.static_server_url = static_server_url;



def listen(port,log_path,log_tag,url_map,static_file_dir,template_dir,static_server_url=None):
    reactor.listenTCP(port,BaseHttpFactory(log_path,log_tag,url_map,static_file_dir,template_dir,static_server_url))
    
def listenSSL(port,log_path,log_tag,url_map,static_file_dir,template_dir, server_key_path, server_crt_path,static_server_url=None):
    factory = BaseHttpFactory(log_path,log_tag,url_map,static_file_dir,template_dir,static_server_url)
    reactor.listenSSL(port, factory, ssl.DefaultOpenSSLContextFactory(server_key_path, server_crt_path))


