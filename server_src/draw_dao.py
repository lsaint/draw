# -*- coding:utf-8 -*-
'''
    file: draw_dao.py
    auth: xuzhijian
    date: 2011-08-30
    desc: 你画我歪dao

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

from mysql_base import *

import logging
import draw_logging

from draw_common import DrawDBConfig
from draw_dictionary import *

from draw_user_mgr import *
from score import *

class DrawDao(object):
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
            print "DrawDao Open Error by disable"
        else:
            print "DrawDao Open ok"
        return self._enable
        
    def LoadUserScore(self,uid):
        if not self._enable:
            return
        
        user = GetDrawUserMgr().GetUserByUid(uid)
        if user is None:
            return
        
        sql = "select id,draw_be_hitted_amount,hitted_amount,good_item_amount,bad_item_amount,first_hitted_amount,master_draw_amount,round_amount,flower_amount,egg_amount from %s where uid = %d" % (DrawDBConfig.DB_DRAW_USER_SCORE_TABLE,uid)
        
        #for debug
        print sql
        
        if self._mysql.Execute(sql, None):
            cursor = self._mysql.Cursor()
            rs = cursor.fetchall()
            if len(rs) != 0:
                row = rs[0]
                if len(row) == 10:#随着上面sql语句里面的field数量而变化
                    user.GetUserScore().Update(row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                    user._bag.NewCategory(OBJ_CATEGORY_FLOWER,DrawObjConfig.OBJ_FLOWER_CAPACITY,int(row[8]))
                    user._bag.NewCategory(OBJ_CATEGORY_EGG,DrawObjConfig.OBJ_EGG_CAPACITY,int(row[9]))
                    return True
        else:
            #to_do some error log
            pass
        return False
        
    def SaveUserScore(self,uid):
        print "try SaveUserScore uid=[%d]" % uid
        if not self._enable:
            return
           
        user = GetDrawUserMgr().GetUserByUid(uid)
        if user is None:
            return
        score = user.GetUserScore()
        flower_amount = user._bag.GetObjAmount(OBJ_CATEGORY_FLOWER)
        egg_amount = user._bag.GetObjAmount(OBJ_CATEGORY_EGG)
                
        sql = "insert into " + DrawDBConfig.DB_DRAW_USER_SCORE_TABLE + " (uid,draw_be_hitted_amount,hitted_amount,good_item_amount,bad_item_amount,first_hitted_amount,master_draw_amount,round_amount,flower_amount,egg_amount) values (%d,%d,%d,%d,%d,%d,%d,%d,%d,%d) ON DUPLICATE KEY UPDATE draw_be_hitted_amount=%d,hitted_amount=%d,good_item_amount=%d,bad_item_amount=%d,first_hitted_amount=%d,master_draw_amount=%d,round_amount=%d,flower_amount=%d,egg_amount=%d" % (uid,score._draw_be_hitted_amount,score._hitted_amount,score._good_item_amount,score._bad_item_amount,score._first_hitted_amount,score._master_draw_amount,score._round_amount,flower_amount,egg_amount,score._draw_be_hitted_amount,score._hitted_amount,score._good_item_amount,score._bad_item_amount,score._first_hitted_amount,score._master_draw_amount,score._round_amount,flower_amount,egg_amount)
        
        print sql
        
        if not self._mysql.Execute(sql, None):
            #to_do some error log
            pass
        
    def LoadDrawDictionary(self):
        if not self._enable:
            return
            
        sql = "select word_str,word_number,word_category,commit_uid,commit_name,channel_id,create_time from %s" % DrawDBConfig.DB_DRAW_DICTIONARY_TABLE
        if self._mysql.Execute(sql, None):
            cursor = self._mysql.Cursor()
            rs = cursor.fetchall()
            if len(rs) != 0:
                for row in rs:
                    if len(row) == 7:#随着上面sql语句里面的field数量而变化
                        from draw_dictionary import *
                        new_word = Word(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                        new_word.SetSaveFlag(False)
                        GetFullDicttionary().AddAWord(new_word)
                        if row[5] != 0:
                            import uid_name
                            uid_name.GetShortChannelIdMgr().NewTopChannel(row[5])
        else:
            #to_do some error log
            pass
        
    def SaveDrawDictionary(self):
        if not self._enable:
            return
            
        para_list = []
        sql = "insert ignore into " + DrawDBConfig.DB_DRAW_DICTIONARY_TABLE +" (word_str,word_number,word_category,commit_uid,commit_name,channel_id) values (%s,%s,%s,%s,%s,%s)"
        for each_word in GetFullDicttionary().GetDictionary().values():
            if each_word.GetSaveFlag():
                one_para = (each_word._word_str, each_word._word_number, each_word._word_category, each_word._word_commit_uid, each_word._word_commit_name, each_word._word_commit_channel,)
                para_list.append( one_para )
        if len(para_list) >= 1:
            if not self._mysql.Execute(sql, para_list):
                #to_do some error log
                pass
               
    def LoadAllChannelDictionary(self):
        if not self._enable:
            return
        
        sql = "select word_str,word_number,word_category,commit_uid,commit_name,channel_id,create_time from %s order by channel_id" % DrawDBConfig.DB_CHANNEL_DICTIONARY_TABLE
        
        if self._mysql.Execute(sql, None):
            cursor = self._mysql.Cursor()
            rs = cursor.fetchall()
            if len(rs) != 0:
                for row in rs:
                    if len(row) == 7:#随着上面sql语句里面的field数量而变化
                        from draw_dictionary import *
                        new_word = Word(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                        new_word.SetSaveFlag(False)
                        GetChannelDictionaryMgr().AddChannelWord(row[5],new_word)
        else:
            #to_do some error log
            pass
    
    def SaveSpecChannelDictionary(self, channel_id, replace_save ):
        if not self._enable:
            return
        
        if replace_save:
            sql = "delete from " + DrawDBConfig.DB_CHANNEL_DICTIONARY_TABLE + " where channel_id = %d" % channel_id
            if not self._mysql.Execute(sql, None):
                #to_do some error log
                pass
                
        para_list = []
        sql = "insert ignore into " + DrawDBConfig.DB_CHANNEL_DICTIONARY_TABLE + " (word_str,word_number,word_category,commit_uid,commit_name,channel_id) values (%s,%s,%s,%s,%s,%s)"
        channel_dictionary = GetChannelDictionaryMgr().GetAllChannelDictionary().get(channel_id)
        if channel_dictionary is not None:
            for each_word in channel_dictionary.GetDictionary().values():
                if replace_save or each_word.GetSaveFlag():
                    one_para = (each_word._word_str, each_word._word_number, each_word._word_category, each_word._word_commit_uid, each_word._word_commit_name, channel_id,)
                    para_list.append( one_para )
            if not self._mysql.Execute(sql, para_list):
                #to_do some error log
                pass
           
    def NewPendingSummitWord(self, new_word):
        if not self._enable:
            return
                
        sql = "insert ignore into " + DrawDBConfig.DB_PENDING_SUMMIT_DICTIONARY_TABLE + " (word_str,word_number,word_category,commit_uid,commit_name,channel_id) values (%s,%s,%s,%s,%s,%s)"
        para_tuple = (new_word._word_str, new_word._word_number, new_word._word_category, new_word._word_commit_uid, new_word._word_commit_name, new_word._word_commit_channel,)
        if not self._mysql.Execute(sql, para_tuple):
            #to_do some error log
            pass
        
    def ApproveSummitWord(self, word_str):
        if not self._enable:
            return
        
g_draw_dao = None
def GetDrawDao():
    global g_draw_dao
    if g_draw_dao is None:
        g_draw_dao = DrawDao()
    return g_draw_dao