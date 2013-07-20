#! /usr/bin/env python
# coding=utf-8
'''
Created on 2012-9-11

@author: ezioruan
'''
import urllib2
import os
import ujson

def download_with_process_status(url,store_dir,file_name=None):
    if not file_name:
        file_path = url.split('/')[-1]
        file_name = file_path.split('=')[-1]
    request = urllib2.urlopen(url)
    download_file = os.path.join(store_dir,file_name)
    print download_file
    with open(download_file,'wb') as f:
        meta = request.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print "Downloading: %s Bytes: %s" % (file_name, file_size)
        
        file_size_download = 0
        block_size = 102400
        while True:
            buffer = request.read(block_size)
            if not buffer:
                break
            file_size_download += len(buffer)
            f.write(buffer)
            download_percent = file_size_download * 100. / file_size
            yield download_percent
    
    
def read_json(url,data=None):
    request = urllib2.Request(url,data,{'Content-Type': 'application/json'})
    response = urllib2.urlopen(request).read()
    return ujson.loads(response)
    
    

if __name__ == '__main__':
#    url = 'https://github.com/twitter/bower/zipball/master'
#    for status in download_with_process_status(url,'D://'):
#        print status
    url = 'http://192.168.1.13'
#    result =  read_json(url)
    download_url = url
    print download_url
    for percent in download_with_process_status(download_url,'D://'):
        print percent

