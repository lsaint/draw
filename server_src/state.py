# -*- coding:utf-8 -*-
'''
    file: state.py
    auth: xuzhijian
    date: 2011-08-13
    desc: 网络画板游戏状态-游戏状态基类以及派生类

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

from draw_pb2 import *
from draw_user_mgr import *
from draw_common import *

import uid_name
import random

from draw_dictionary import *

class State(object):
    def __init__(self,channel):
        self._end_time = 0
        self._state_id = APPLY_STATE
        self._game_mode_id = STANDRAD_TURN
        self._cur_status = False
        self._channel = channel
        
    def GetChn(self):
        return self._channel
 
    def GetStateId(self):
        return self._state_id
        
    def SetStateId(self, state_id):
        self._state_id = state_id
        
    def GetGameModeId(self):
        return self._game_mode_id
        
    def SetGameModeId(self, game_mode_id):
        self._game_mode_id = game_mode_id
        
    def StateStart(self,timer_time):
        self._cur_status = True
        
    def StateStop(self):
        self._cur_status = False
        
    def GetStateStatus(self):
        return self._cur_status
        
    def OnTimer(self,timer_time):
        pass

class EstimateState(State):
    def __init__(self,channel):
        State.__init__(self,channel)
        self.SetStateId(ESTIMATE_STATE)
        self.SetGameModeId(STANDRAD_TURN)
        
    def StateStart(self,timer_time):
        State.StateStart(self, timer_time)
        self._end_time = timer_time + DrawStateConfig.ESTIMATE_STATE_DURATION
        self.GetChn().StandardEstimateStateStart()
       
    def OnTimer(self,timer_time):
        if self.GetStateStatus():
            if timer_time > self._end_time:
                self.GetChn().GetCurMode().SetNextState(timer_time)
       
class ApplyState(State):
    def __init__(self,channel):
        State.__init__(self,channel)
        self._apply_list = {}
        self._apply_poll = []
        self._apply_max_amount = DrawStateConfig.APPLY_MAX_AMOUNT
        self.SetStateId(APPLY_STATE)
        self.SetGameModeId(STANDRAD_TURN)
        
    def InitApplyPool(self):
        self._apply_poll = []
        for roll_point in range(0,101):
            self._apply_poll.append(roll_point)

    def GetValidRollPoint(self):
        amount = len(self._apply_poll)
        if amount <= 0:
            return 0
        target_id = random.randint(0,amount-1)
        return self._apply_poll.pop(target_id)
            
    def UserApply(self,uid):
        res = ds2dc_apply_drawer_response()
        
        if uid not in self.GetChn()._watcher_dict.keys():
            return
        elif len(self._apply_list) >= DrawStateConfig.APPLY_MAX_AMOUNT:
            res.apply_response = res.FAIL_FULL_APPLICANT
        elif uid in self._apply_list.keys():
            res.apply_response = res.FAIL_APPLY_ALREADY
        else:
            res.apply_response = res.OK
            
            #roll_point = random.randint(0,100)
            roll_point = self.GetValidRollPoint()
            self._apply_list[uid] = roll_point
            res.roll_point = roll_point
            
            notification_res = ds2dc_apply_drawer_notification()
            notification_res.uid = uid
            notification_res.roll_point = roll_point
            self.GetChn().SendMsgToDrawChannelUsrs(uid, notification_res)
            
        GetDrawUserMgr().SendMessage(uid, self.GetChn()._topchannel_id, res)
            
    def ClearApplyUser(self):
        self._apply_list = {}
        
    def GetApplyList(self):
        return self._apply_list
        
    def StateStart(self,timer_time):
        State.StateStart(self, timer_time)
        self._end_time = 0
        self.ClearApplyUser()
        self.GetChn().StandardApplyStateStart()
        self.InitApplyPool()
        
    def OnTimer(self,timer_time):
        if self.GetStateStatus():
            if len(self._apply_list) > 0 and self._end_time == 0:
                self._end_time = timer_time + DrawStateConfig.APPLY_STATE_DURATION
            if self._end_time > 0 and timer_time > self._end_time:
                self.GetChn().GetCurMode().SetNextState(timer_time)
        
class GameState(State):
    def __init__(self,channel):
        State.__init__(self,channel)
        self._hit_keyword_users_list = []
        self._first_hit = False
        self._first_hit_uid = 0
        self._start_time = 0
        self._end_time = 0
        self._key_word = ''
        self.SetStateId(GAME_STATE)
        self.SetGameModeId(STANDRAD_TURN)
        
    def DoHitKeyword(self, uid):
        self._hit_keyword_users_list.append(uid)
        
        chat_notification_res = ds2dc_chat_notification()
        chat_notification_res.from_uid = 0
        chat_notification_res.chat_mode = SYSTEM_CHAT
        full_msg = '%s 歪中了答案！' % uid_name.GetUidNameMgr().GetUserName(uid).encode('utf-8')
        chat_notification_res.chat_msg = full_msg.decode('utf-8')
        self.GetChn().SendMsgToDrawChannelUsrs(0, chat_notification_res)
    
        #猜中者积分变化
        user = GetDrawUserMgr().GetUserByUid(uid)
        if user is not None:
            if len(self._hit_keyword_users_list) <= 1:
                user.GetUserScore().FirstHitThisRound()
                self.GetChn()._score_mgr.FirstHitThisRound(uid)
            else:
                user.GetUserScore().HitThisRound()
                self.GetChn()._score_mgr.HitThisRound(uid)
            
        #画画者积分变化
        drawer = GetDrawUserMgr().GetUserByUid(self.GetChn()._master_id)
        if drawer is not None:
            drawer.GetUserScore().DrawBeHitted()
            self.GetChn()._score_mgr.DrawBeHitted(drawer._uid)
        
    def CheckKeyword(self, uid, dc2ds_chat_request_obj):
        if dc2ds_chat_request_obj.chat_msg.strip() == self.GetKeyWord().str():
            #主笔玩家说出答案不算胜利，同时也不按照普通聊天显示
            if self.GetChn()._master_id == uid:
                return True
            elif uid not in self._hit_keyword_users_list:
                    self.DoHitKeyword(uid)
                    #if len(self._hit_keyword_users_list) >= self.GetChn().GetWatcherAmount():
                    #    for watcher_id in self.GetChn()._watcher_dict.keys():
                    #        if watcher_id not in self._hit_keyword_users_list:
                    #            return True
                        #全部观战用户都猜中了，神人 =_=!
                    #    self.GetChn().GetCurMode().SetNextState(0)
                    return True
            else:
                #已经猜中的玩家，又再次输入正确答案，不显示
                return True
        elif dc2ds_chat_request_obj.chat_msg.replace(' ','').find(self.GetKeyWord().str()) != -1 and self.GetChn()._master_id == uid:
            dc2ds_chat_request_obj.chat_msg = dc2ds_chat_request_obj.chat_msg.replace(' ','').replace(self.GetKeyWord().str(), '****')
        
        return False
  
    def GetRewardRate(self, duration):
        # [40,60]秒-80%,  [30,40]秒-50%, [20,30]秒-20%, [0,20]秒-0%
        rate = 0
        if duration > 40000:
            rate = 80
        elif duration > 30000:
            rate = 50
        elif duration > 20000:
            rate = 20
        return rate
        
    def GetRandomRewardType(self):
        reward_obj_type = OBJ_CATEGORY_FLOWER
        if random.randint(1,100) < 50:
            reward_obj_type = OBJ_CATEGORY_EGG
        return reward_obj_type
        
    def SendOneRandomReward(self, uid):
        user = GetDrawUserMgr().GetUserByUid(uid)
        reward_obj_type = self.GetRandomRewardType()
        reward_obj_amount = 1
        if user is not None:
            res = ds2dc_gain_item_notification()
            res.uid = uid
            res.item_type = reward_obj_type
            res.amount = reward_obj_amount
            if user.ChangeObjAmount(reward_obj_type,reward_obj_amount):
                res.operation_result = res.OK
            else:
                res.operation_result = res.FAIL_CATEGORY_FULL
            #暂时只是发送给自己    
            user.SendMessage(self.GetChn()._topchannel_id , res)
        
    def RoundReward(self, duration):
        rate = self.GetRewardRate(duration)
        effect_rate = rate
        print "RoundReward rate=%d duration=%d" % (effect_rate,duration)
        for uid in self._hit_keyword_users_list:
            if uid == self._first_hit_uid:
                effect_rate = rate + DrawObjConfig.OBJ_FIRST_HIT_REWARD_RATE_BONUS
            else:
                effect_rate = rate
            if random.randint(1,100) < effect_rate:
                self.SendOneRandomReward(uid)
            
    def StateStop(self):
        State.StateStop(self)
        
        duration = self._end_time - self._start_time
        self.RoundReward(duration)
        
        self.GetChn().StandardGameStateStop()
  
    def StateStart(self,timer_time):
        State.StateStart(self, timer_time)
        self._hit_keyword_users_list = []
        self._first_hit = False
        self._first_hit_uid = 0
        
        dict_rate = self.GetChn()._runtime_data.GetChannelDictionaryRate()
        rate_roll = random.randint(1,100)
        
        if len( GetChannelDictionaryMgr().GetAChannelDictionary(self.GetChn()._channel_id).GetDictionary() ) <= 1:
            self._key_word = GetFullDicttionary().PickAWord()
        elif rate_roll < 25:
            if dict_rate == CHANNEL_DICTIONARY_RATE_LOW or dict_rate == CHANNEL_DICTIONARY_RATE_MIDDLE or dict_rate == CHANNEL_DICTIONARY_RATE_HIGH:
                self._key_word = GetChannelDictionaryMgr().GetAChannelDictionary( self.GetChn()._channel_id ).PickAWord()
            else:
                self._key_word = GetFullDicttionary().PickAWord()
        elif rate_roll < 50:
            if dict_rate == CHANNEL_DICTIONARY_RATE_MIDDLE or dict_rate == CHANNEL_DICTIONARY_RATE_HIGH:
                self._key_word = GetChannelDictionaryMgr().GetAChannelDictionary( self.GetChn()._channel_id ).PickAWord()
            else:
                self._key_word = GetFullDicttionary().PickAWord()
        elif rate_roll < 75:
            if dict_rate == CHANNEL_DICTIONARY_RATE_HIGH:
                self._key_word = GetChannelDictionaryMgr().GetAChannelDictionary( self.GetChn()._channel_id ).PickAWord()
            else:
                self._key_word = GetFullDicttionary().PickAWord()
        else:
            self._key_word = GetFullDicttionary().PickAWord()
        
        if self.GetChn().StandardGameStateStart():
            self._end_time = timer_time + DrawStateConfig.GAME_STATE_DURATION
            self._start_time = timer_time
        
    def GetKeyWord(self):
        return self._key_word
    
    def DoTimerFirstHit(self,timer_time,uid):
        self._first_hit = True
        self._first_hit_uid = uid
        
        #回合剩余时间 vs 首中后的10秒，取小者
        if self._end_time > timer_time + DrawStateConfig.GAME_FIRST_HIT_REMAINING_TIME:
            self._end_time = timer_time + DrawStateConfig.GAME_FIRST_HIT_REMAINING_TIME
            
        remaining_time = ( self._end_time - timer_time ) / 1000
        if remaining_time < 0 or remaining_time > DrawStateConfig.GAME_FIRST_HIT_REMAINING_SEC:
            remaining_time = DrawStateConfig.GAME_FIRST_HIT_REMAINING_SEC
            
        notification_res = ds2dc_first_hit_keyword_notification()
        notification_res.first_hit_uid = uid
        notification_res.remaining_time = remaining_time
        self.GetChn().SendMsgToDrawChannelUsrs(0, notification_res)
                    
    def OnTimer(self,timer_time):
        if self.GetStateStatus():
            if not self._first_hit and len(self._hit_keyword_users_list) >= 1:
                self.DoTimerFirstHit(timer_time,self._hit_keyword_users_list[0])
            if timer_time > self._end_time or self.GetChn()._master_id == 0:
                self.GetChn().GetCurMode().SetNextState(timer_time)
                
class AlternationEstimateState(State):
    def __init__(self,channel):
        State.__init__(self,channel)
        self.SetStateId(ALTERNATION_ESTIMATE_STATE)
        self.SetGameModeId(ALTERNATION_TURN)
        
    def StateStart(self,timer_time):
        State.StateStart(self, timer_time)
        self._end_time = timer_time + DrawStateConfig.ALTERNATION_ESTIMATE_STATE_DURATION
        self.GetChn().AlternationEstimateStateStart()
       
    def OnTimer(self,timer_time):
        if self.GetStateStatus():
            if timer_time > self._end_time:
                self.GetChn().BeginRound(timer_time)
                self.GetChn().GetCurMode().SetNextState(timer_time)
                
class AlternationGameState(State):
    def __init__(self,channel):
        State.__init__(self,channel)
        self.SetStateId(ALTERNATION_GAME_STATE)
        self.SetGameModeId(ALTERNATION_TURN)
        
    def StateStart(self,timer_time):
        State.StateStart(self, timer_time)
        self._end_time = timer_time + DrawStateConfig.ALTERNATION_GAME_STATE_DURATION
        self.GetChn().AlternationGameStateStart()
       
    def OnTimer(self,timer_time):
        if self.GetStateStatus():
            if timer_time > self._end_time or self.GetChn()._master_id == 0:
                self.GetChn().EndRound(timer_time)      
                self.GetChn().GetCurMode().SetNextState(timer_time)
                
class PresidingDrawState(State):
    def __init__(self,channel):
        State.__init__(self,channel)
        self.SetStateId(PRESIDING_DRAW_STATE)
        self.SetGameModeId(PRESIDING_TURN)
        
    def StateStart(self,timer_time):
        State.StateStart(self, timer_time)
        self.GetChn().PresidingDrawStateStart()
       
    def OnTimer(self,timer_time):
        pass
        