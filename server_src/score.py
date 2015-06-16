# -*- coding:utf-8 -*-
'''
    file: score.py
    date: 2011-08-17
    desc: 网络画板标准模式 用户分数类

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

import time
import uid_name
from draw_pb2 import *

from draw_user_mgr import *

#鲜花、鸡蛋、首中、歪中、主笔次数、游戏局数、被歪中次数
class UserScore(object):
    def __init__(self, uid):
        self._first_hit_this_round = False
        self._hit_this_round = False
        self._uid = uid
        
        self._draw_be_hitted_amount = 0           #被歪中次数
        self._hitted_amount = 0                   #歪中

        self._good_item_amount = 0                #鲜花数
        self._bad_item_amount = 0                 #鸡蛋数
        self._first_hitted_amount = 0             #首中数
        self._master_draw_amount = 0              #主笔次数
        self._round_amount = 0                    #游戏局数
        
        self.LoadScoreFromDB()
        
    def LoadScoreFromDB(self):
        from draw_dao import *
        GetDrawDao().LoadUserScore(self._uid)
        
    def Update(self, draw_be_hitted_amount, hitted_amount, good_item_amount, bad_item_amount, first_hitted_amount, master_draw_amount, round_amount):
        self._draw_be_hitted_amount = draw_be_hitted_amount
        self._hitted_amount = hitted_amount
        self._good_item_amount = good_item_amount
        self._bad_item_amount = bad_item_amount
        self._first_hitted_amount = first_hitted_amount
        self._master_draw_amount = master_draw_amount
        self._round_amount = round_amount
        
    def ClearRoundScore(self):
        self._first_hit_this_round = False
        self._hit_this_round = False
        
    def FirstHitThisRound(self):
        self._first_hit_this_round = True
        self._first_hitted_amount = self._first_hitted_amount + 1
        
    def HitThisRound(self):
        self._hit_this_round = True
        self._hitted_amount = self._hitted_amount + 1
        
    def ReceiveGoodItem(self,amount):
        self._good_item_amount = self._good_item_amount + amount
        
    def ReceiveBadItem(self,amount):
        self._bad_item_amount = self._bad_item_amount + amount
        
    def DrawBeHitted(self):
        self._draw_be_hitted_amount = self._draw_be_hitted_amount + 1
        
    def OneRound(self, is_master):
        if is_master:
            self._master_draw_amount = self._master_draw_amount + 1
        self._round_amount = self._round_amount + 1
        
class ChannelUserScore(UserScore):
    def __init__(self, uid):
        UserScore.__init__(self,uid)
        self._name = uid_name.GetUidNameMgr().GetUserName(uid)
    
    def LoadScoreFromDB(self):
        return
    
        
class ChannelScoreMgr(object):
    def __init__(self, channel_obj):
        self._channel = channel_obj
        self._enable = False
        self._last_op_time = 0
        self._last_op_uid = 0
        self._last_op_name = ""
        self._start_time = 0
        self._end_time = 0
        self._user_score_list = {}
        
    def AddAUser(self, uid, chn_user_score = None):
        if self.GetStatus():
            if chn_user_score is None:
                chn_user_score = ChannelUserScore(uid)
                
            self._user_score_list[uid] = chn_user_score
            return chn_user_score
        
        return None
        
    def GetAUser(self, uid):
        if self.GetStatus() and not self._user_score_list.has_key(uid):
            self.AddAUser(uid)
        return self._user_score_list.get(uid)
        
    def GetAllUser(self):
        return self._user_score_list
        
    def GetAmount(self):
        return len(self._user_score_list)
        
    def Stop(self, uid):
        if self.GetStatus():
            self.SetStatus(False)
            name = ""
            if uid != 0:
                name = uid_name.GetUidNameMgr().GetUserName(uid)
            self._last_op_uid = uid
            self._last_op_name = name
            self._last_op_time = int(time.time())
            
            res = ds2dc_stop_action_notification()
            res.operation_uid = uid
            res.operation_name = name
            self._channel.SendMsgToDrawChannelUsrs( 0, res )
        
    def Start(self, uid, duration):
        if not self.GetStatus():
            self.SetStatus(True)
            name = uid_name.GetUidNameMgr().GetUserName(uid)
            self._last_op_uid = uid
            self._last_op_name = name
            self._last_op_time = int(time.time())
            self._start_time = self._last_op_time
            self._end_time = self._last_op_time + duration
            self.ClearAllScore()
            
            res = ds2dc_start_action_notification()
            res.operation_uid = uid
            res.operation_name = name
            res.start_time = self._start_time
            res.end_time = self._end_time
            self._channel.SendMsgToDrawChannelUsrs( 0, res )

    def SendChnScoreNotification(self, target_uid):
        print "SendChnScoreNotification channel=%d target_uid=%d" % (self._channel._topchannel_id, target_uid)
    
        chn_score_res = ds2dc_chn_action_score_notification()
        chn_all_user_score = self.GetAllUser()
        for uid in chn_all_user_score.keys():
            user_score = chn_score_res.user_score_list.add()
            user_score.uid = uid
            user_score.first_hit_this_round = chn_all_user_score[uid]._first_hit_this_round
            user_score.hit_this_round = chn_all_user_score[uid]._hit_this_round
            user_score.draw_be_hitted_amount = chn_all_user_score[uid]._draw_be_hitted_amount
            user_score.hitted_amount = chn_all_user_score[uid]._hitted_amount
            user_score.first_hitted_amount = chn_all_user_score[uid]._first_hitted_amount
            user_score.good_item_amount = chn_all_user_score[uid]._good_item_amount
            user_score.bad_item_amount = chn_all_user_score[uid]._bad_item_amount
            from draw_user_mgr import *
            user = GetDrawUserMgr().GetUserByUid(uid)
            if user is not None:
                user_score.online = True
                user_score.name = user.GetUserName()
            else:
                user_score.online = False
                user_score.name = uid_name.GetUidNameMgr().GetUserName(uid)
                
        if target_uid == 0:
            self._channel.SendMsgToDrawChannelUsrs( 0, chn_score_res )
        else:
            from draw_main import *
            GetDrawMainMgr().SendMessage( target_uid, self._channel._topchannel_id, chn_score_res )
            
    def UserEnterChnScoreNotification(self, uid):    
        res = ds2dc_start_action_notification()
        res.operation_uid = self._last_op_uid
        res.operation_name = self._last_op_name
        res.start_time = self._start_time
        res.end_time = self._end_time
        
        from draw_user_mgr import *
        GetDrawUserMgr().SendMessage(uid, self._channel._topchannel_id, res )
    
        self.SendChnScoreNotification(uid)
    
    def ActionOnTimer(self, stand_time):            
        if self.GetStatus() and not self.ActionTimeCheck(stand_time):
            self.Stop(0)
    
    def ActionTimeCheck(self,stand_time):
        if stand_time >= self._end_time or self._end_time < self._start_time:
            return False
        return True
        
    def ClearAllScore(self):
        self._user_score_list.clear()
        
    def GetStatus(self):
        return self._enable
        
    def SetStatus(self,status):
        self._enable = status
        
    def FirstHitThisRound(self,uid):
        if self.GetStatus():
            self.GetAUser(uid).FirstHitThisRound()
        
    def HitThisRound(self,uid):
        if self.GetStatus():
            self.GetAUser(uid).HitThisRound()
        
    def ReceiveGoodItem(self,uid,amount):
        if self.GetStatus():
            self.GetAUser(uid).ReceiveGoodItem(amount)
        
    def ReceiveBadItem(self,uid,amount):
        if self.GetStatus():
            self.GetAUser(uid).ReceiveBadItem(amount)
        
    def DrawBeHitted(self,uid):
        if self.GetStatus():
            self.GetAUser(uid).DrawBeHitted()
        
    def OneRound(self, uid, is_master):
        if self.GetStatus():
            self.GetAUser(uid).OneRound(is_master)
            
    def ClearRoundScore(self,uid):
        if self.GetStatus():
            self.GetAUser(uid).ClearRoundScore()