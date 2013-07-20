#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 2012-7-15

@author:  adaws
'''
import sys, traceback, linecache

def format_exc():
    """
    Print the usual traceback information, followed by a listing of all the
    local variables in each frame.
    """
    class ValueError:pass
    etype, value, tb = sys.exc_info()
    result_str_lst = ['']
    locals_lst = []
    while tb is not None:
        need_locals = tb.tb_next is None
        error_info, locals_str = get_frame_data(tb, need_locals)
        result_str_lst.append(error_info)
        if need_locals:locals_lst.append(locals_str)

        tb = tb.tb_next

    result_str_lst += traceback.format_exception_only(etype, value)
    return '\n\t'.join(result_str_lst), '\n\t'.join(locals_lst)


def get_frame_data(tb, need_locals=False):
    frame = tb.tb_frame
    co = frame.f_code
    filename = co.co_filename
    name = co.co_name
    lineno = tb.tb_lineno
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, frame.f_globals)
    line_data = line and line.strip() or 'None'

    result_str = "%s  ==>  %s  " % (("%s(%s)" % (filename, str(lineno)))[-100:], "In(%s)  %s" % (name, line_data))

    return result_str, get_locals_data(frame, need_locals)

def get_locals_data(frame, need_locals=False):
    if not need_locals:return ''
    tmp_str_lst = ['']
    for key, value in frame.f_locals.items():
        str_value = None
        try:
            if type(value) == str:
                str_value = '"%s"'%str(value)
            else:
                str_value = str(value)
        except:
            str_value = ValueError

        tmp_str_lst.append("%s = %s" % (key, str_value))

    local_info_msg = '\n\t'.join(tmp_str_lst)
    return local_info_msg


def C():
    a = 2
    a *=2
    c = 1/0
    print c
    
if __name__ == '__main__':
    try:
        C()
    except:
        print format_exc()[0]
        print format_exc()[1]
        