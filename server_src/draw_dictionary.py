# -*- coding:utf-8 -*-
'''
    file: draw_dictionary.py
    auth: xuzhijian
    date: 2011-08-17
    desc: 网络画板游戏词库基类以及派生类

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

import time
import random
from draw_common import DrawDictConfig
from draw_dao import *

from draw_user_mgr import *

class Word(object):
    def __init__(self, word_str, word_number, word_category, word_commit_uid, word_commit_name, word_commit_channel, create_time):
        self._word_str = word_str.strip().decode('utf-8')
        self._word_number = word_number
        self._word_category = word_category
        self._word_commit_uid = word_commit_uid
        self._word_commit_name = word_commit_name.decode('utf-8')
        self._word_commit_channel = word_commit_channel
        if create_time is None:
            self._create_time = int(time.time())
        else:
            self._create_time = create_time
        self._hit_count = 0
        self._need_save = True

    def str(self):
        return self._word_str

    def SetSaveFlag(self, new_save_flag):
        self._need_save = new_save_flag
        
    def GetSaveFlag(self):
        return self._need_save
        
    def IsSystemWord(self):
        if self._word_commit_uid == 0:
            return True
            
        return False
        
    def SystemWord(self):
        self._word_commit_uid = 0
        self._word_commit_name = ''
        self._word_commit_channel = 0
               
class Dictionary(object):
    def __init__(self):
        self._dictionary = {}
        self._enable = False
        
    def SimulateLoadWords(self):
        new_word1 = Word("苹果", 2, DrawDictConfig.CATEGORY_FRUIT, 0, '', 0, None)
        self.AddAWord(new_word1)
        
        new_word2 = Word("台灯", 2, DrawDictConfig.CATEGORY_FURNITURE, 0, '', 0, None)
        self.AddAWord(new_word2)
        
        new_word3 = Word("老虎", 2, DrawDictConfig.CATEGORY_ANIMAL, 0, '', 0, None)
        self.AddAWord(new_word3)
        
        new_word4 = Word("下雨", 2, DrawDictConfig.CATEGORY_NATURA, 0, '', 0, None)
        self.AddAWord(new_word4)
        
    def GetDictionary(self):
        return self._dictionary
        
    def LoadDictionaryFromFile(self, file_path, word_number):
        dict_file = open(file_path)
        if dict_file is None:
            print 'open dict file %s fail' % file_path
        try:
            for line in dict_file:
                new_word = Word(line, word_number, DrawDictConfig.CATEGORY_UNKNOWN, 0, '', 0, None)
                if not self.AddAWord(new_word):
                    print 'LoadDictionaryFromFile Add = %s fail' % line.strip()
        finally:
            dict_file.close()
        
    def InitDict(self):
        if not self._enable:
            self.SimulateLoadWords()
            self._enable = True
        
    def LoadDictionaryFromDB(self):
        pass
        
    def PickAWord(self):
        #to_do 未来可以把命中次数太少的词优先提取
        word_amount = len(self._dictionary)
        if word_amount < 1:
            return None
        random_index = random.randint(0,word_amount-1)
        return self._dictionary.values()[random_index]
        
    def CanAddAWord(self, check_word):
        if check_word._word_str not in self._dictionary.keys():
            return True
        
        return False  
        
    def AddAWord(self, new_word):
        if new_word._word_str not in self._dictionary.keys():
            self._dictionary[new_word._word_str] = new_word
            return True
        
        return False
        
    def RemoveAWord(self, remove_word):
        if remove_word._word_str not in self._dictionary.keys():
            del self._dictionary[remove_word._word_str]
    
    def ClearAllWords(self):
        self._dictionary = {}
        
class FullDictionary(Dictionary):
    def __init__(self):
        Dictionary.__init__(self)

    def LoadDictionaryFromDB(self):
        GetDrawDao().LoadDrawDictionary()
               
    def InitDict(self):
        if not self._enable:
            self.LoadDictionaryFromDB()
            self.LoadDictionaryFromFile('draw/server_src/dict6.txt', 6)
            self.LoadDictionaryFromFile('draw/server_src/dict5.txt', 5)
            self.LoadDictionaryFromFile('draw/server_src/dict4.txt', 4)
            self.LoadDictionaryFromFile('draw/server_src/dict3.txt', 3)
            self.LoadDictionaryFromFile('draw/server_src/dict2.txt', 2)
            #self.SimulateLoadWords()
            print "SystemDictionary init finish, word amount = %d" % len(self._dictionary)
            self._enable = True
    
class ChannelDictionary(Dictionary):
    def __init__(self, channel_id ):
        Dictionary.__init__(self)
        self._channel_id = channel_id
        
    def LoadDictionaryFromDB(self):
        pass

    def GetChannelId(self):
        return self._channel_id
                
class ChannelDictionaryMgr(object):
    def __init__(self):
        self._channel_dictionary = {}
        self._enable = False
        
    def GetAChannelDictionary(self, channel_id):
        channel_dictionary = self.GetSpecChannelDictionary(channel_id)
        if channel_dictionary is None:
            channel_dictionary = ChannelDictionary(channel_id)
            self._channel_dictionary[channel_id] = channel_dictionary
        return channel_dictionary
        
    def GetSpecChannelDictionary(self, channel_id):
        return self._channel_dictionary.get(channel_id)

    def AddChannelWord(self, channel_id, new_word):
        self.GetAChannelDictionary(channel_id).AddAWord(new_word)
    
    def GetAllChannelDictionary(self):
        return self._channel_dictionary
        
    def LoadDictionaryFromDB(self):
        GetDrawDao().LoadAllChannelDictionary()
        
    def InitDict(self):
        if not self._enable:
            self.LoadDictionaryFromDB()
            self._enable = True
            
    def OnManageChannelWords(self, uid, yychannel_id, yysubchannel_id, dc2ds_manage_channel_words_request_obj):
        #print "OnManageChannelWords uid=%d, yychannel_id=%d, yysubchannel_id=%d" % (uid,yychannel_id,yysubchannel_id)
        res = ds2dc_manage_channel_words_response()        
        if not self.CheckAuthority(uid, yysubchannel_id):
            res.manage_channel_words_response = res.FAIL_ERROR_OP_AUTHORITY
        else:
            res.manage_channel_words_response = res.OK
            
            channel_dictionary = GetChannelDictionaryMgr().GetAChannelDictionary(yysubchannel_id)
            if channel_dictionary is not None:
                for each_word in channel_dictionary.GetDictionary().values():
                    res.words.append( each_word.str() )

        GetDrawUserMgr().SendMessage(uid,yychannel_id,res)
        #to_do 是否需要上个一段时间的独占锁？2个管理人员同时提交会发生互相覆盖的问题
       
    def DoUpdateChannelWords( self, uid, yychannel_id, yysubchannel_id, dc2ds_update_channel_words_request_obj):
        channel_dictionary = self.GetAChannelDictionary( yysubchannel_id )
        channel_dictionary.ClearAllWords()
        user = GetDrawUserMgr().GetUserByUid( uid )
        #to_do add some log 
        for each_word_str in dc2ds_update_channel_words_request_obj.words:
            if len(each_word_str.strip()) != 0:
                new_word = Word(each_word_str, len(each_word_str)/3, DrawDictConfig.CATEGORY_UNKNOWN, uid, user.GetUserName(), yysubchannel_id, None)
                channel_dictionary.AddAWord(new_word)
            
        GetDrawDao().SaveSpecChannelDictionary(yysubchannel_id, True)
       
    def OnUpdateChannelWords(self, uid, yychannel_id, yysubchannel_id, dc2ds_update_channel_words_request_obj ):
        #print "OnUpdateChannelWords uid=%d, yychannel_id=%d, yysubchannel_id=%d" % (uid,yychannel_id,yysubchannel_id)
    
        res = ds2dc_update_channel_words_response()
            
        if not self.CheckAuthority(uid, yysubchannel_id):
            res.update_channel_words_response = res.FAIL_ERROR_OP_AUTHORITY
        elif len(dc2ds_update_channel_words_request_obj.words) > DrawDictConfig.MAX_CHANNEL_DICTIONARY_WORDS_AMOUNT:
            res.update_channel_words_response = res.FAIL_ERROR_EXCEED_LIMIT
        else:
            res.update_channel_words_response = res.OK
            self.DoUpdateChannelWords( uid, yychannel_id, yysubchannel_id, dc2ds_update_channel_words_request_obj)
        GetDrawUserMgr().SendMessage(uid,yychannel_id,res)
        
    def DoAddChannelWords( self, uid, yysubchannel_id, add_word_list):
        channel_dictionary = self.GetAChannelDictionary( yysubchannel_id )
        for each_word in add_word_list:            
            channel_dictionary.AddAWord(each_word)
            
        GetDrawDao().SaveSpecChannelDictionary(yysubchannel_id, False)
        
    def OnSubmitWords(self, uid, yychannel_id, yysubchannel_id, dc2ds_submit_words_request_obj ):
        #print "OnSubmitWords uid=%d, yychannel_id=%d, yysubchannel_id=%d type=%d" % (uid,yychannel_id,yysubchannel_id,dc2ds_submit_words_request_obj.submit_words_type)
    
        user = GetDrawUserMgr().GetUserByUid( uid )
        
        if user is not None:
            if dc2ds_submit_words_request_obj.submit_words_type == dc2ds_submit_words_request_obj.CUSTUM_DICTIONARY or dc2ds_submit_words_request_obj.submit_words_type == dc2ds_submit_words_request_obj.BOTH:
                for each_word_str in dc2ds_submit_words_request_obj.words:
                    if len(each_word_str.strip()) != 0 and len(each_word_str.strip()) <= DrawDictConfig.MAX_DICTIONARY_WORDS_LEN:
                        #print "NewPendingSummitWord = [%s]" % each_word_str.strip()
                        new_word = Word(each_word_str, len(each_word_str)/3, DrawDictConfig.CATEGORY_UNKNOWN, uid, user.GetUserName(), yychannel_id, None)
                        GetDrawDao().NewPendingSummitWord(new_word)
                        
            if dc2ds_submit_words_request_obj.submit_words_type == dc2ds_submit_words_request_obj.CHANNEL_DICTIONARY or dc2ds_submit_words_request_obj.submit_words_type == dc2ds_submit_words_request_obj.BOTH:
                if self.CheckAuthority(uid, yysubchannel_id):
                    new_word_list = []
                    for each_word_str in dc2ds_submit_words_request_obj.words:
                        if len(each_word_str.strip()) != 0 and len(each_word_str.strip()) <= DrawDictConfig.MAX_DICTIONARY_WORDS_LEN:
                            #print "DoAddChannelWords = [%s]" % each_word_str.strip()
                            new_word = Word(each_word_str, len(each_word_str)/3, DrawDictConfig.CATEGORY_UNKNOWN, uid, user.GetUserName(), yysubchannel_id, None)
                            if self.GetAChannelDictionary(yysubchannel_id).CanAddAWord(new_word):
                                new_word_list.append(new_word)
                    
                    if len(new_word_list) > 0:
                        self.DoAddChannelWords(uid, yysubchannel_id, new_word_list)
        
    def CheckAuthority(self, uid, yychannel_id):
        import chl_usr
        from authority import *
        role = chl_usr.GetAllUsrChlRoleMgr().GetUsrChlRole(uid, yychannel_id)
        return GetAuthorityMgr().GetMasterTypeAuthority(role)
    
    
    
g_channel_dictionary_mgr = None
def GetChannelDictionaryMgr():
    global g_channel_dictionary_mgr
    if g_channel_dictionary_mgr is None:
        g_channel_dictionary_mgr = ChannelDictionaryMgr()
    return g_channel_dictionary_mgr
   
g_full_dictionary = None
def GetFullDicttionary():
    global g_full_dictionary
    if g_full_dictionary is None:
        g_full_dictionary = FullDictionary()
    return g_full_dictionary