# -*- coding:utf-8 -*-
'''
    file: mysql_base.py
    auth: xuzhijian
    date: 2011-08-30
    desc: mysql基础类

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

import MySQLdb

import logging
import draw_logging

class mysql_base(object):
    def __init__(self):
        self._db_conn = None
        self._db_host = ''
        self._db_port = ''
        self._db_name = ''
        self._db_user = ''
        self._db_passwd = ''
        self._cursor = None
        self._logger = logging.getLogger(draw_logging.DB_LOG)

    def Stop(self):
        if self._cursor is not None:
            self._cursor.close()
        if self._db_conn is not None:
            self._db_conn.close()
            
        self._cursor = None
        self._db_conn = None
  
    def Open(self, dbhost, dbport, dbname, dbuser, dbpasswd):
        try:
            self._db_conn = MySQLdb.connect(
                            host=dbhost,
                            port=dbport,
                            user=dbuser,
                            passwd=dbpasswd,
                            db=dbname,
                            init_command="set names utf8",
                            charset="utf8")
        except Exception, e:
            self._logger.error("error ! Connect to database fail : %s" % e)
            self._db_conn = None
            return False
        if self._db_conn is not None:
            self._db_conn.set_character_set('utf8')
            self._cursor = self._db_conn.cursor()
            self._logger.info("Connect to database success")
            print self._db_conn.character_set_name()
            return True
        else:
            self._logger.info("Connect to database Fail")
            return False

    def Cursor(self):
        return self._cursor
            
    def Execute(self, sql, parameter):
        if not self._db_conn or not self._cursor:
            return False
        
        try:
            if parameter is not None:
                if isinstance(parameter, tuple):
                    self._cursor.execute(""+sql+"", parameter)
                elif isinstance(parameter, list):
                    self._cursor.executemany(""+sql+"", parameter)
                else:
                    self._logger.error("Execute sql \"%s\" error parameter type: %s", sql, type(parameter))
                    return False
            else:
                self._cursor.execute(""+sql+"")
            self._db_conn.commit()
        except Exception, e:
            self._logger.error("Execute sql \"%s\" error : %s", sql, e)
            self._cursor.close()
            self._db_conn.close()
            self._db_conn = None
            return False
        return True
        
        