#! /usr/bin/env python
# coding=utf-8
'''
Created on 2013-02-19

@author: adaws
@note: 检查脏字引擎
'''

import os
_check_hash_dct = {}
_max = 0


#---使用该 系统 要先使用初始化---
def init_bad_word_check_sys(file_path=None):
    _check_hash_dct.clear()
    
    if file_path == None:
        file_path = os.path.join(os.path.dirname(__file__), 'BadWord.txt')
        
    bad_word_file = open(file_path, 'r')
    
    for word in bad_word_file.readlines():
#        if not word.strip():break
        add_word(word)

#---增加屏蔽词---
def add_word(word):
    global _max
    
    add_lst = list(word.strip().decode('utf-8'))
    if len(add_lst) > _max:
        _max = len(add_lst)
        
    start_dct = _check_hash_dct
    for i in add_lst:
        start_dct = start_dct.setdefault(i, {})
    
    start_dct[0]=1

#如果有脏字返回False 否则返回True
def check(word):
    word_lst = list(word.strip().decode('utf-8'))
    word_lenth = len(word_lst)
    
    start = 0
    
    #---开启test_times 可以查看查找次数---
    #test_times = 0
    
    while start < word_lenth:
        cur_pos = start
        start_dct = _check_hash_dct
        
        find = False
        while 1:
            #test_times +=1
            if cur_pos >= word_lenth:
                break
            
            cur_word = word_lst[cur_pos]
            start_dct = start_dct.get(cur_word)
            if not start_dct:
                break
                
            if 0 in start_dct:
                #print 'CheckAt', word_lst[start:cur_pos+1], ''.join(word_lst[start:cur_pos+1])
                return False
            cur_pos += 1
            
        if find:
            start = cur_pos + 1
        else:
            start += 1
    
    return True

def replace(word, replace_c ='*'):
    word_lst = list(word.strip().decode('utf-8'))
    word_lenth = len(word_lst)
    
    res_lst = []
    start = 0
    
    #---开启test_times 可以查看查找次数---
    #test_times = 0
    
    while start < word_lenth:
        cur_pos = start
        start_dct = _check_hash_dct
        
        find = False
        while 1:
            #test_times +=1
            if cur_pos >= word_lenth:
                break
            
            cur_word = word_lst[cur_pos]
            start_dct = start_dct.get(cur_word)
            if not start_dct:
                break
                
            if 0 in start_dct:
                #print 'CheckAt', word_lst[start:cur_pos+1], ''.join(word_lst[start:cur_pos+1])
                res_lst.append((start, cur_pos+1))
                find = True
                break
            
            cur_pos += 1
            
        if find:
            start = cur_pos + 1
        else:
            start += 1
    
    if not res_lst or (not replace_c):
        return word
    
    replaced_word_lst = []
    cur = 0
    for start, end in res_lst:
        replaced_word_lst.append(''.join(word_lst[cur:start]))
        replaced_word_lst.append(replace_c*(end-start))
#        if end-start>3:
#            replaced_word_lst.append(word_lst[start]+(end-start-2)*replace_c+word_lst[end-1])
#        else:
#            replaced_word_lst.append((end-start-1)*replace_c+word_lst[end-1])
        
        cur = end
            
    replaced_word_lst.append(''.join(word_lst[end:]))
    
    #print 'TestTimes', test_times
    return ''.join(replaced_word_lst)
    
    

def test():
    init_bad_word_check_sys()
    #print ''.join(_check_hash_dct.keys())
    
    import sys
    
    print sys.getsizeof(_check_hash_dct)
    
    import pprint
    #pprint.pprint(_check_hash_dct)
    print _max

    import time
    start = time.time()
    data = None
    test_cnt = 10000
    check_content = '你大爷 youareasb SM 肛 hdw 江泽民 毛泽东 哈哈哈哈哈 我操 操你妈FUCK good ni malgb wocao le Sm'
    for i in xrange(test_cnt):
        data = replace(check_content)
        check_res = check(check_content)
    print data
    print check_res
    print 'Test Times(%s) Cost(%s)'%(test_cnt, time.time()-start)


if __name__ == '__main__':
    test()





