# -*- coding:utf-8 -*-
'''
    file: draw_user_mgr.py
    date: 2011-06-28
    desc: 网络画板用户理器

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

import uid_name
from score import UserScore
from draw_common import DrawConfig
from draw_pb2 import *
from inventory import *
from draw_dao import *

import logging
import draw_logging

class DrawUser(object):
    def __init__(self, uid, watch = True):
        self._uid = uid
        self._name = uid_name.GetUidNameMgr().GetUserName(uid)
        self._watch = watch
        self._last_channel = None
        self._ping_flag = True
        self._online_flag = True
        self._location = INDIVIDUAL_CHANNEL_ROOM
        self._last_save_time = 0
        
        self._bag = Bag(DrawObjConfig.BAG_INVENTORY_CAPACITY)
        self._score = UserScore(uid)
                                    
    def InitObj(self):
        self._bag.NewCategory(OBJ_CATEGORY_FLOWER,DrawObjConfig.OBJ_FLOWER_CAPACITY,DrawObjConfig.OBJ_FLOWER_CAPACITY)
        self._bag.NewCategory(OBJ_CATEGORY_EGG,DrawObjConfig.OBJ_EGG_CAPACITY,DrawObjConfig.OBJ_EGG_CAPACITY)
                                    
    def OnTimer(self,timer_time):
        if self._last_save_time == 0:
            self._last_save_time = timer_time
           
        if timer_time - self._last_save_time >= DrawConfig.MAX_USER_SAVE_TIME:
            DrawUserMgr._logger.info("user save uid=[%d]" % self._uid )
            self._last_save_time = timer_time
            from draw_dao import *
            GetDrawDao().SaveUserScore(self._uid)
                      
    def ChangeObjAmount(self, category_id, delta):
        return self._bag.ChangeObjAmount(category_id, delta)
        
    def GetObjAmount(self, category_id):
        return self._bag.GetObjAmount(category_id)
                
    def SetUserLocationFlag(self, location):
        self._location = location

    def GetUserLocationFlag(self):
        return self._location
                
    def SetOnlineFlag(self, flag):
        self._online_flag = flag
                
    def GetOnlineFlag(self):
        return self._online_flag
                
    def SetPingFlag(self, flag):
        self._ping_flag = flag
        
    def GetPingFlag(self):
        return self._ping_flag
        
    def GetUserScore(self):
        return self._score
        
    def SetUserLastChannel(self, channel):
        self._last_channel = channel
        self.GetUserScore().ClearRoundScore()
        channel._score_mgr.ClearRoundScore(self._uid)
        
    def GetUserLastChannel(self):
        return self._last_channel
        
    def SetUserWatchFlag(self, watch):
        self._watch = watch

    def GetUserWatchFlag(self):
        return self._watch
        
    def SetUserName(self, name):
        self._name = name
    
    def SetUserImid(self, imid):
        self._imid = imid

    def GetUserName(self):
        return self._name
        
    def SendMessage(self, yychannel_id, msg):
        from draw_main import *
        GetDrawMainMgr().SendMessage( self._uid, yychannel_id, msg )
        
class DrawUserMgr(object):
    _full_user_dict = {}
    _amount = 0
    _last_check_time = 0
    _logger = logging.getLogger(draw_logging.LOGIC_DEBUG_LOG)

    def GetUsersAmount(self):
        return DrawUserMgr._amount
    
    def NewUser(self, uid):
        if not DrawUserMgr._full_user_dict.has_key(uid):
            user = DrawUser(uid)
            DrawUserMgr._full_user_dict[uid] = user
            DrawUserMgr._amount = DrawUserMgr._amount + 1
            
            from draw_dao import *
            if not GetDrawDao().LoadUserScore(uid):
                user.InitObj()
            return user
        return DrawUserMgr._full_user_dict[uid]
            
    def RemoveUser(self, uid):
        if DrawUserMgr._full_user_dict.has_key(uid):
            DrawUserMgr._full_user_dict[uid].SetOnlineFlag(False)
            del DrawUserMgr._full_user_dict[uid]
            if DrawUserMgr._amount >= 1:
                DrawUserMgr._amount = DrawUserMgr._amount - 1
            
    def GetUserByUid(self, uid):
        if not DrawUserMgr._full_user_dict.has_key(uid):
            return None
        return DrawUserMgr._full_user_dict[uid]
    
    def SendMessage(self, uid, yychannel_id, msg):
        from draw_main import *
        GetDrawMainMgr().SendMessage( uid, yychannel_id, msg )
        
    def OnTimer(self,timer_time):
        if DrawUserMgr._last_check_time == 0:
            DrawUserMgr._last_check_time = timer_time
        if timer_time - DrawUserMgr._last_check_time >= DrawConfig.MAX_PING_IDLE_TIME:
            DrawUserMgr._logger.info("idle timer check timer_time=[%d] online=[%d]" % (timer_time,DrawUserMgr._amount) )
            DrawUserMgr._last_check_time = timer_time
            kick_list = []
            res = ds2dc_quit_notification()
            res.quit_type = res.SYSTEM_REBOOT
        
            for user in DrawUserMgr._full_user_dict.values():
                if user.GetPingFlag():
                    user.SetPingFlag(False)
                else:
                    kick_list.append(user)
                    
                user.OnTimer(timer_time)
            
            for need_kick_user in kick_list:
                last_channel = need_kick_user.GetUserLastChannel()
                if last_channel is not None:
                    from draw_channel_mgr import *
                    GetDrawChannelMgr().OnUserLeaveDraw(need_kick_user._uid, last_channel._channel_id)
                    DrawUserMgr._logger.info("kick idle user Channel=[%d] TopChannel=[%d] uid=[%d]" % (last_channel._channel_id, last_channel._topchannel_id, need_kick_user._uid))
        
    def OnPing(self,uid):
        user = self.GetUserByUid(uid)
        if user is not None:
            user.SetPingFlag(True)
            DrawUserMgr._logger.info("OnPing ok uid=[%d]" % uid )
            
    def GetScoreRequest(self,uid,yychannel_id,yysubchannel_id,dc2ds_get_score_request_obj):
        user = self.GetUserByUid(uid)
        from draw_channel_mgr import *
        if user is not None:
            res = ds2dc_get_score_response()
            res.target_type = dc2ds_get_score_request_obj.target_type
            if dc2ds_get_score_request_obj.target_type == TARGET_MASTER_DRAWER:
                channel = GetDrawChannelMgr().GetDrawChannelByChannelId(yysubchannel_id)
                if channel is not None:
                    res.target_uid = channel.GetMasterDrawId()
                    #if res.target_uid == 0:
                    #    res.target_uid = self._last_master_id
                else:
                    res.target_uid = uid
            elif dc2ds_get_score_request_obj.target_type == TARGET_SELF:
                res.target_uid = uid
            elif dc2ds_get_score_request_obj.target_type == TARGET_UID:
                if dc2ds_get_score_request_obj.HasField('target_uid'):
                    res.target_uid = dc2ds_get_score_request_obj.target_uid
                else:
                    res.target_uid = uid
            target_user = self.GetUserByUid(res.target_uid)
            if target_user is None:
                res.response_type = res.FAIL_ERROR_TARGET
                res.draw_be_hitted_amount = 0
                res.hitted_amount = 0
                res.good_item_amount = 0
                res.bad_item_amount = 0
                res.first_hitted_amount = 0
                res.master_draw_amount = 0
                res.round_amount = 0
                res.flower_amount = 0
                res.egg_amount = 0
            else:
                res.response_type = res.OK
                res.draw_be_hitted_amount = target_user.GetUserScore()._draw_be_hitted_amount
                res.hitted_amount = target_user.GetUserScore()._hitted_amount
                res.good_item_amount = target_user.GetUserScore()._good_item_amount
                res.bad_item_amount = target_user.GetUserScore()._bad_item_amount
                res.first_hitted_amount = target_user.GetUserScore()._first_hitted_amount
                res.master_draw_amount = target_user.GetUserScore()._master_draw_amount
                res.round_amount = target_user.GetUserScore()._round_amount
                res.flower_amount = target_user._bag.GetObjAmount(OBJ_CATEGORY_FLOWER)
                res.egg_amount = target_user._bag.GetObjAmount(OBJ_CATEGORY_EGG)
                DrawUserMgr._logger.info("Get Score ok uid=[%d] flower=[%d] egg=[%d] round=[%d]" % (uid,res.flower_amount,res.egg_amount,res.round_amount) )
            user.SendMessage(yychannel_id, res)
            
g_dumgr = None
def GetDrawUserMgr():
    global g_dumgr
    if g_dumgr is None:
        g_dumgr = DrawUserMgr()
    return g_dumgr