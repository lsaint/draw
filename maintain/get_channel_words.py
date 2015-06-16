# -*- coding:utf-8 -*-

from mysql_base import *

class SummitWordsDao(object):
    def __init__(self):
        self._mysql = mysql_base()
        self._host = ''
        self._port = 0
        self._name = ''
        self._user = ''
        self._passwd = ''
        self._enable = False
        
    def Open(self, dbhost, dbport, dbname, dbuser, dbpasswd):
        self._host = dbhost
        self._port = dbport
        self._name = dbname
        self._user = dbuser
        self._passwd = dbpasswd
        self._enable = self._mysql.Open(self._host, self._port, self._name, self._user, self._passwd)
        if not self._enable:
            print "SummitWordsDao Open Error by disable"
        else:
            print "SummitWordsDao Open ok"
        return self._enable
        
    def Stop(self):
        self._enable = False
        self._mysql.Stop()
        
    def LoadSummitWords(self):
        if not self._enable:
            return
            
        #sql = "select id,word_str,word_number,word_category,commit_uid,commit_name,channel_id,create_time from app_draw_channel_dictionary"
        sql = "select id,word_str,channel_id from app_draw_channel_dictionary"
        if self._mysql.Execute(sql, None):
            cursor = self._mysql.Cursor()
            rs = cursor.fetchall()
            if len(rs) != 0:
                for row in rs:
                    if len(row) == 3:#随着上面sql语句里面的field数量而变化
                        #print "%d %s %d %d %d %s %d" % (row[0],row[1],row[2],row[3],row[4],row[5],row[6])
                        print "%d %s %d" % (row[0],row[1],row[2])
        else:
            print "Execute sql error"
            return
            
if __name__ == "__main__":
    dao = SummitWordsDao()
    print dao.Open('127.0.0.1', 6208, 'app_db', 'root', '&2Hk9&Vbx@Aa')
    #print dao.Open('127.0.0.1', 3306, 'app_db', 'root', '218')
    dao.LoadSummitWords()
    dao.Stop()
    