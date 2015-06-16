# -*- coding:utf-8 -*-
'''
    file: web_dao.py
    auth: xuzhijian
    date: 2011-10-15
    desc: 你画我歪 web_dao

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

from mysql_base import *
from web_common import WebDBCommon

class WebDao(object):
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
            print "WebDao Open Error by disable"
        else:
            print "WebDao Open ok"
        return self._enable
        
    def LoadImageLocation(self,topchannel):
        if not self._enable:
            print "LoadImageLocation Error by disable"
            return
        
        images_list = []
        topchannel_id = int(topchannel)
        
        if topchannel_id < 0:
            #载入创意图集
            sql = "select id,topchannel,location,file_name,name,keyword,shortchannel_id from %s where flag > 1 order by flag,create_time desc limit 30" % (WebDBCommon.WEB_APP_DB_TABLE)
        elif topchannel_id != 0:
            sql = "select id,topchannel,location,file_name,name,keyword,shortchannel_id from %s where topchannel = %d order by create_time desc limit 3" % (WebDBCommon.WEB_APP_DB_TABLE,topchannel_id)
        else:
            sql = "select id,topchannel,location,file_name,name,keyword,shortchannel_id from %s order by create_time desc limit 3" % (WebDBCommon.WEB_APP_DB_TABLE)
            
        if self._mysql.Execute(sql, None):
            cursor = self._mysql.Cursor()
            rs = cursor.fetchall()
            if len(rs) != 0:
                for row in rs:
                    if len(row) == 7:#随着上面sql语句里面的field数量而变化
                        images_list.append([row[1],row[2]+row[3],row[4].decode("utf-8"),row[5].decode("utf-8")],row[6])
        else:
            #to_do some error log
            pass
            
        return images_list
        
    def SaveImageLocation(self,uid,name,keyword, channel_id, topchannel,location,file_name, shortchannel_id):
        if not self._enable:
            return False
                
        sql = "insert ignore into " + WebDBCommon.WEB_APP_DB_TABLE + " (uid,name,keyword,channel_id,topchannel,location,file_name,shortchannel_id) values (%d,'%s','%s',%d,%d,'%s','%s',%d)" % (uid,name,keyword, channel_id, topchannel,location,file_name,shortchannel_id)
        
        # 以后要换用这种方式，有助于去除用户可能的模仿访问
        #sql = "insert ignore into " + WebDBCommon.WEB_APP_DB_TABLE + " (uid,name,keyword,channel_id,topchannel,location,file_name) values (%d,'%s','%s',%d,%d,'%s','%s')"
        #param_tuple = (uid,name,keyword, channel_id, topchannel,location,file_name)
        #if not self._mysql.Execute(sql, param_tuple):
        
        if not self._mysql.Execute(sql, None):
            #to_do some error log
            return False
        
        return True
        
        
g_web_dao = None
def GetWebDao():
    global g_web_dao
    if g_web_dao is None:
        g_web_dao = WebDao()
    return g_web_dao