# -*- coding:utf-8 -*-
'''
    file: standard_mode.py
    author: lSaint
    date: 2011-08-12
    desc: 标准模式 系统出题

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

from dialog_score import ScoreWindow
from draw_pb2 import *
from common import *
from PyQt4 import QtCore



class StandardModeMgr(object):

    def __init__(self, game, window, connection):
        self.window = window
        self.game = game
        self.connection = connection
        self.chat_mgr = game.chat_mgr
        self.score_window = ScoreWindow(game, window)
        self.CreateConnection()
        self.is_fresher = True
        self.Reset()


    def Reset(self):
        self.score_window.Reset()
        self.uid_dice = {}
        self.last_host_uid = None
        self.keyword = ""


    def CheckFresherTip(self, is_show):
        if not is_show:
            return self.window.AnimateArrow(False)
            
        if self.is_fresher and is_show:
            self.window.AnimateArrow(True)
            self.is_fresher = False


    def CreateConnection(self):
        self.window.button_ret.clicked.connect(self.OnClickButtonRet)
        #self.score_window.button_save.clicked.connect(self.window.DefaultSave)

    
    def RegisterStandardModeCallback(self):
        self.connection.AddHandler(ds2dc_apply_state, self.OnApplyState)
        self.connection.AddHandler(ds2dc_apply_drawer_response, self.OnApplyHostResponse)
        self.connection.AddHandler(ds2dc_apply_drawer_notification, self.OnApplyHostNotification)
        self.connection.AddHandler(ds2dc_game_state, self.OnStartStandardRound)
        self.connection.AddHandler(ds2dc_first_hit_keyword_notification, self.OnFirstHitKeyWordNotification)
        self.connection.AddHandler(ds2dc_estimate_state, self.OnGuessResult)
        self.score_window.RegisterScoreCallback()


    def OnClickButtonRet(self):
        self.score_window.Show()


    def OnGameModeChanged(self, mode):
        self.window.label_keyword.setText("")
        self.window.observer_list.Shuffle()
        if mode != draw_pb2.STANDRAD_TURN:
            self.window.button_ret.setDisabled(True)
        else:
            self.window.button_ret.setDisabled(False)

    
    def GetKeyword(self):
        return self.keyword

    def SetWatcherKeyword(self,word):
        self.keyword = word
        
    def SetKeyword(self, word):
        self.window.label_keyword.setText(word)
        self.game.ShowTip(u"画题：%s" % word)
        self.keyword = word

    #def ShowKeyword(self, word):
    #    self.score_window.label_answer.setText(word)


    def ClearKeyword(self):
        self.window.label_keyword.setText("")
        self.keyword = ""


    def ShowPlayerDice(self, uid, num):
        self.window.observer_list.SetDice(uid, num)
        self.window.observer_list.sortItems(COL_DICE, QtCore.Qt.DescendingOrder)


    def SetStandardModeHost(self, uid):
        self.game.SetHost(uid, False)
        self.window.player_list.SetDice(uid, self.uid_dice.get(uid, ""))
        self.last_host_uid = uid


    def RoundClear(self):
        self.uid_dice = {}
        self.window.observer_list.Shuffle()
        #self.score_window.Clear()
        self.ClearKeyword()


    # 开始扔骰子
    def OnApplyState(self, pb):
        print "OnApplyState", pb.state_second, pb.apply_amount
        self.game.Countdown(pb.state_second)
        self.chat_mgr.ShowSystemTip(u"本回合已开始，请点击加入按钮掷骰子，\
                前%d位中点数最大的玩家将成为本轮主笔。" % pb.apply_amount)
        self.CheckFresherTip(True)
        self.game.EnterRestState()


    # 扔骰子回应
    def OnApplyHostResponse(self, pb):
        print "OnApplyHostResponse", pb.OK
        #OK = 1;
        #FAIL_NOT_IN_STANDARD_TYPE = 2;
        #FAIL_NOT_IN_APPLY_STATE = 3;
        #FAIL_FULL_APPLICANT = 4;
        #FAIL_ROLL_CD = 5;
        #FAIL_APPLY_ALREADY = 6;
        if pb.apply_response == pb.OK:
            self.ShowPlayerDice(self.game.uid, pb.roll_point)
            self.uid_dice[self.game.uid] = pb.roll_point
        elif pb.apply_response == pb.FAIL_NOT_IN_STANDARD_TYPE:
            self.game.chat_mgr.ShowAnnounce(u"模式错误")
        elif pb.apply_response == pb.FAIL_NOT_IN_APPLY_STATE:
            self.game.chat_mgr.ShowAnnounce(u"现在还不能争夺主笔")
        elif pb.apply_response == pb.FAIL_FULL_APPLICANT:
            self.game.chat_mgr.ShowAnnounce(u"名额已满")
        elif pb.apply_response == pb.FAIL_ROLL_CD:
            self.game.chat_mgr.ShowAnnounce(u"扔骰子过于频繁，请稍候。")


    # 扔骰子广播
    def OnApplyHostNotification(self, pb):
        print "OnApplyHostNotification"
        self.ShowPlayerDice(pb.uid, pb.roll_point)
        self.uid_dice[pb.uid] = pb.roll_point


    # 开始标准模式的一轮
    def OnStartStandardRound(self, pb):
        print "OnStartStandardRound"
        self.ClearKeyword()
        self.window.scribbleArea.clearImage()
        self.game.SetGameRole(pb.drawer_id, PLAYER_ROLE)
        self.SetStandardModeHost(pb.drawer_id)
        self.game.Countdown(pb.round_second)
        if self.game.uid == pb.drawer_id:
            self.SetKeyword(pb.key_word)
        else:
            self.SetWatcherKeyword(pb.key_word)
        self.CheckFresherTip(False)


    # 有人答中
    def OnFirstHitKeyWordNotification(self, pb):
        print "OnFirstHitKeyWordNotification"#, pb.uid, pb.remaining_time
        name = self.game.uid_name.get(pb.first_hit_uid, "")
        self.chat_mgr.ShowSystemTip(u"<font color='magenta'>%s</font>率先歪中了答案,真给力！剩余%d秒。"\
                % (name, pb.remaining_time))
        self.game.Countdown(pb.remaining_time)
 

    # 一轮结果
    def OnGuessResult(self, pb):
        print " OnGuessResult"
        self.RoundClear()
        answer = u"本回合答案为：<font color='magenta'>%s</font>" % pb.last_keyword
        if pb.HasField("word_commit_name"):
            answer  = u"%s 提交者:%s 提交频道:%s" % (answer, pb.word_commit_name, pb.word_commit_channel)
        self.chat_mgr.ShowSystemTip(answer)
        #for us in pb.user_score_list:
        #    self.score_window.AddLine(us.uid, us.first_hit_this_round, us.hit_this_round,\
        #            us.draw_be_hitted_amount, us.hitted_amount, us.good_item_amount, us.bad_item_amount)
        # 进入评价状态
        self.game.EnterAppriseState()


    # roll点抢位
    def ThrowDice(self):
        print "ThrowDice"
        self.connection.SendPb(dc2ds_apply_drawer_request())


    def StandardModeAppraise(self):
        print "StandardModeAppraise"
        self.window.button_draw.setEnabled(False)
        if self.game.uid == self.last_host_uid:
            self.game.appraise_panel.Hide()

