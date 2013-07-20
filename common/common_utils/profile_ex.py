#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2012-11-28

@author:  adaws
非Main模块块的profile
'''

import cProfile as profile
import __main__
import pstats
import os

def test_profile(func):
    def _func(*args, **kwargs):
        profile_file_path = os.path.join(os.path.dirname(__file__), '%s_data.txt'%func.__name__)
        
        tuple_par_lst = []
        for par_index, par in enumerate(args):
            __main__.__dict__['par_%s'%par_index] = par
            tuple_par_lst.append('par_%s'%par_index)
        
        tuple_par_str = ','.join(tuple_par_lst)
        
        kw_par_lst = []
        for key, value in kwargs.items():
            key_value_name = 'key_value_name_%s'%key
            __main__.__dict__[key_value_name] = value
            kw_par_lst.append("%s=%s"%(key, key_value_name))
            
        kw_par_str = ','.join(kw_par_lst)
        
        func_name = 'test_%s'%func.__name__
        __main__.__dict__[func_name] = func
        
        run_str = "%s(%s, %s)"%(func_name, tuple_par_str, kw_par_str)
        
        
        profile.run(run_str, profile_file_path)
        statpf = open(os.path.join(os.path.dirname(__file__), "%s_statics.txt"%func.__name__), 'w+')
        p = pstats.Stats(profile_file_path, stream=statpf)
        p.strip_dirs().sort_stats("cumulative").print_stats()
        statpf.close()
    
    return _func

if __name__ == '__main__':
    import time
    def B(sec):
        time.sleep(sec)
        
    def A(times, sleep, k=1, g=2):
        cnt = 0
        for i in xrange(10000*times):
            cnt += i
        
        B(sleep)
    
        B(k*g)
        print k,g
        
        
    a = test_profile(A)
    
    a(10, 0.3)
