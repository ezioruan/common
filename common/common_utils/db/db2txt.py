#! /usr/bin/env python
# coding=utf-8
'''
Created on 2013-5-14

@author: Ezio Ruan
'''
from common.common_utils import db_operator
import os
import codecs



def convert_data2txt(db_host,db_port,db_username,db_password,db_name,out_dir=''):
    information_schema_connection = db_operator.DB_Conn(db_host=db_host, db_port=db_port, db_username=db_username, db_password=db_password, db_name='information_schema', dict_cursor=True)
    db_connection = db_operator.DB_Conn(db_host=db_host, db_port=db_port, db_username=db_username, db_password=db_password, db_name=db_name, dict_cursor=True)
    get_all_table_sql = """
        SELECT TABLE_NAME FROM TABLES WHERE TABLE_SCHEMA = '%s'
    """ % db_name
    for table in information_schema_connection.read_db(get_all_table_sql):
        table_name = table['TABLE_NAME']
        file_path = os.path.join(out_dir,'%s.txt' % table_name)
        with codecs.open(file_path, 'w', 'utf-8') as f:
            get_table_column_sql = """
            SELECT COLUMN_NAME,COLUMN_TYPE,COLUMN_COMMENT FROM COLUMNS 
            WHERE TABLE_SCHEMA = '%s' AND TABLE_NAME = '%s'
            """ %  (db_name,table_name)
            table_desc = ''
            column_list = []
            for column in information_schema_connection.read_db(get_table_column_sql):
                table_desc += '%s\t%s\t%s\n' % (column['COLUMN_NAME'],column['COLUMN_TYPE'],column['COLUMN_COMMENT'])
                column_list.append(column['COLUMN_NAME'])
            div_line = '#-------------------------------------------------------------------------------------\n'
            header = '\t'.join(column_list)
            get_data_sql = """
            SELECT * FROM %s 
            """ % table_name
            data = ''
            for table_data in db_connection.read_db(get_data_sql):
                data+= '\t'.join([str(table_data[column]) if table_data[column] != None else ''  for column in column_list]) + '\n'
            f.write(table_desc+div_line+header+'\n'+data)

    


if __name__ == '__main__':
    convert_data2txt('192.168.1.42',3306,'root','6772492','ezio_base','E://AptanaWorkSpace//server//data//db_base_tables')