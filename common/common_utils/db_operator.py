#!/usr/bin/ python
# coding=utf-8

from DBUtils.PooledDB import PooledDB
from MySQLdb.cursors import DictCursor, Cursor
import MySQLdb
import types
from MySQLdb import escape_string as db_text
import datetime

class NoPool(object):
        def __init__(self, db_cnf_ins):
            self.conn = db_cnf_ins.get_conn()
            self.close = self.conn.close
            self.conn.close = lambda * arg:None

        def connection(self):
            return self.conn

class DB_Conn(object):
    ATTR_DEFAULT_LST = [
                        ('db_host', '127.0.0.1'),
                        ('db_port', 3306),
                        ('db_name', ''),
                        ('db_username', ''),
                        ('db_password', ''),
                        ('use_pool', True),
                        ('min_cached', 1),
                        ('max_cached', 20),
                        ('max_shared', 1),
                        ('max_connections', 0),
                        ('blocking', False),
                        ('max_usage', 1000),
                        ('set_session', None),
                        ('reset', True),
                        ('failures', None),
                        ('ping', 1),
                        ('time_out', 2073600),
                        ('dict_cursor', True),
                        ('err_file', None),
                        ]


    #是否使用连接池 use_pool 发布的服务器一开始可能没多少人玩 还是开启pool 后期可以考虑定期ping的形式而不用连接池 使用连接池带来的性能损耗是比较大的
    def __init__(self, **kwarg):
        for attr, default in self.ATTR_DEFAULT_LST:
            if not kwarg.has_key(attr):
                self.__dict__[attr] = default
            else:
                self.__dict__[attr] = kwarg[attr]

        self._conn = None
        self._pool = None

    def get_conn(self):
        if self._conn:return self._conn
        use_cursor =  self.dict_cursor and DictCursor or Cursor
        self._conn = MySQLdb.connect(host=self.db_host, port=self.db_port, \
                               user=self.db_username, passwd=self.db_password, \
                               db=self.db_name, use_unicode=True, charset='utf8', \
                               cursorclass=use_cursor)

        #设置当前连接超时时间 单位分钟 主要是db服务器改时间 可以造成连接过期
        cursor = self._conn.cursor()
        cursor.execute("set interactive_timeout=%s;" % self.time_out)
        cursor.execute("set wait_timeout=%s;" % self.time_out)
        cursor.close()
        return self._conn

    def get_connection(self):
        if not self._pool:self._create_pool()
        return self._pool.connection()

    def _create_pool(self):
        if self.use_pool:
            use_cursor =  self.dict_cursor and DictCursor or Cursor
            self._pool = PooledDB(MySQLdb, mincached=self.min_cached, maxcached=self.max_cached, \
                            maxshared=self.max_shared, maxconnections=self.max_connections, \
                            blocking=self.blocking, maxusage=self.max_usage, \
                            setsession=self.set_session, reset=self.reset, \
                            failures=self.failures, ping=self.ping, \
                            host=self.db_host, port=self.db_port, \
                            user=self.db_username, passwd=self.db_password, \
                            db=self.db_name, use_unicode=True, charset='utf8', \
                            cursorclass=use_cursor)
        else:
            self._pool = NoPool(self)

    def get_pool(self):
        if not self._pool:self._create_pool()
        return self._pool


    def read_db(self, sql):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(sql)
        ret = cur.fetchall()
        cur.close()
        conn.close()
        return ret

    def write_db(self, sql_set):
        '''
        写接口 不需返回ID(可以对多表操作)
        @param sql_set: SQL语句集合
        '''
        # 从连接池获取一个连接
        conn = self.get_connection()
        cur = conn.cursor()
        is_success = False
        try:
            if type(sql_set) == types.ListType:
                # 多条语句
                for sql in sql_set:
                    cur.execute(sql)

            elif type(sql_set) in types.StringTypes:
                # 单条语句
                cur.execute(sql_set)

        except Exception, e:
            self.record_err(sql_set, e)
            conn.rollback()

        else:
            conn.commit()
            is_success = True

        cur.close()
        conn.close()
        return is_success
        

    def write_db_return_last_id(self, sql_set):
        '''
        单写并返回ID
        '''
        # 从连接池获取一个连接
        conn = self.get_connection()
        cur = conn.cursor()
        
        sucess = True
        try:
            if type(sql_set) == types.ListType: return
    
            elif type(sql_set) in types.StringTypes:
                # 单条语句
                cur.execute(sql_set)
                
        except Exception, e:
            self.record_err(sql_set, e)
            conn.rollback()
            sucess = False
        else:
            conn.commit()
    
        last_id = cur.lastrowid if sucess else -1
        cur.close()
        conn.close()
        return last_id

    def multi_write_db(self, sql, param):
        '''
        写接口, 对同一个表操作多条记录, 不需返回ID
        @param sql: 要操作的SQL格式(sql = 'INSERT INTO t2(money, gold) VALUES(%s, %s)')
        @param param: List or Tuple(param = [(100, 1000), (200, 2000)])
        '''
        # 从连接池获取一个连接
        conn = self.get_connection()
    
        cur = conn.cursor()
        sucess = True
        if type(param) not in [types.ListType, types.TupleType]:
            param = [param]
        try:
            cur.executemany(sql, param)
    
        except Exception, e:
            sucess = False
            self.record_err(sql, e, 'with par %s'%str(param))
            conn.rollback()
    
        else:
            conn.commit()
        last_id = cur.lastrowid if sucess else -1
        cur.close()
        conn.close()
        return last_id
    
    def multile_write_db_return_last_id(self, sql_set):
        '''
        多写并返回ID集合(对同个表的操作)
        @param sql_set:
        '''
        conn = self.get_connection()
    
        cur = conn.cursor()
    
        last_insert_id_list = []
    
        try:
            if type(sql_set) != types.ListType: return
            # 多条语句
            for sql in sql_set:
                cur.execute(sql)
    
                last_insert_id_list.append(cur.lastrowid)
    
        except Exception, e:
            self.record_err(sql, e)
            conn.rollback()
            last_insert_id_list = []
    
        else:
            conn.commit()
    
        cur.close()
    
        return last_insert_id_list
    
    def record_err(self, sql, e, other_msg=''):
        if not self.err_file or self.err_file.closed:return
        self.err_file.write('[%s]: sql] (%s)\n error] %s | msg(%s) other(%s)\n'%(datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"), sql, str(e), e.message, other_msg))
        self.err_file.flush()
        
        
    def call_store_procs(self,store_procs_name,args):
        conn = self.get_connection()
        cursor =conn.cursor()
        cursor.callproc(store_procs_name,args)
        result_set = cursor.fetchall()
        cursor.close()
        conn.close()
        return result_set
