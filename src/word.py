# -*- coding:utf-8 -*-
'''
    file: word.py
    author: lSaint
    date: 2011-8-29
    desc: 词库模块

    广州华多网络科技有限公司 版权所有 (c) 2005-2010 DuoWan.com [多玩游戏]
'''

from common import *
import draw_pb2
from draw_pb2 import *
from dialog_word import WordWindow


class WordMgr(object):

    def __init__(self, game, window):
        self.game = game
        self.window = window
        self.connection = game.connection
        self.chlword_rate = draw_pb2.CHANNEL_DICTIONARY_RATE_LOW 


    def SetChlWordRate(self, rate):
        self.chlword_rate = rate


    def CreateWordWindow(self):
        self.dialog_word = WordWindow(self.window, self.game)


    def RegisterSumitWordCallback(self):
        self.connection.AddHandler(ds2dc_manage_channel_words_response, self.OnShowChlWordResponse)
        self.connection.AddHandler(ds2dc_update_channel_words_response, self.OnUpdateChlWordResponse)


    def OnShowChlWordResponse(self, pb): 
        print "OnShowChlWordResponse", pb.manage_channel_words_response 
        if pb.manage_channel_words_response == pb.OK:
           self.dialog_word.OnShowChlWords(pb.words)
        elif pb.manage_channel_words_response == pb.FAIL_MANAGE_CD:
            self.dialog_word.ShowChlTip(u"编辑过于频繁，请稍候。")
        else:
            self.dialog_word.ShowChlTip(u"你没有编辑权限。")


    def OnUpdateChlWordResponse(self, pb):
        print "OnUpdateChlWordResponse", pb.update_channel_words_response 
        if pb.update_channel_words_response == pb.OK:
            tip = u"编辑成功"
        elif pb.update_channel_words_response == pb.FAIL_UPDATE_CD:
            tip = u"编辑过于频繁，请稍候。"
        elif pb.update_channel_words_response == pb.FAIL_ERROR_OP_AUTHORITY:
            tip = u"你没有编辑权限"
        elif pb.update_channel_words_response == pb.FAIL_ERROR_EXCEED_LIMIT:
            tip = u"字数过多"

        self.dialog_word.ShowChlTip(tip)

    
    # 请求频道词库列表
    def RequestShowChlWords(self):
        print "RequestShowChlWords"
        pb = dc2ds_manage_channel_words_request()
        self.connection.SendPb(pb)

    
    # 请求更新频道词库
    def RequestUpdateChannelWords(self, words):
        print "RequestUpdateChannelWords"
        pb = dc2ds_update_channel_words_request()
        pb.words.extend(words)
        self.connection.SendPb(pb)


    # 提交频道
    def RequestSumitChlWords(self, words):
        print "RequestSumitChlWords", words
        pb = dc2ds_submit_words_request()
        pb.submit_words_type = pb.CHANNEL_DICTIONARY
        pb.words.extend(words)
        self.connection.SendPb(pb)


    # 提交系统
    def RequestSumitSysWords(self, words):
        print "RequestSumitSysWords", words
        if words == ['']:
            return False
        pb = dc2ds_submit_words_request()
        pb.submit_words_type = pb.CUSTUM_DICTIONARY
        pb.words.extend(words)
        self.connection.SendPb(pb)
        return True

    
    # 修改频道词频
    def RequestSetChlWordRate(self, rate):
        print "RequestSetChlWordRate", rate
        pb = dc2ds_config_request()
        pb.config_mode = draw_pb2.CONFIG_SET_CHANNEL_DICTIONARY_RATE 
        pb.channel_dictionary_rate = rate
        self.connection.SendPb(pb)


    def OnSetChlWordRateResponse(self, pb):
        print "OnSetChlWordRateResponse", pb.channel_dictionary_rate
        self.chlword_rate = pb.channel_dictionary_rate
        self.game.chat_mgr.ShowAnnounce(u"你已设置频道词库使用概率为：%s。"\
                % NAME_CHL_WORD_RATE[self.chlword_rate])


    def OnSetChlWordRateNotification(self, pb):
        print "OnSetChlWordRateNotification", 
        self.game.chat_mgr.ShowAnnounce(u"频道词库使用概率被%s设置为：%s。"\
               % (self.game.GetUsrName(pb.op_uid), NAME_CHL_WORD_RATE[pb.channel_dictionary_rate]))



