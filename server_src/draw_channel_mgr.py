# -*- coding:utf-8 -*-
'''
    file: draw_channel_mgr.py
    date: 2011-06-28
    desc: 网络画板频道管理器

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

import chl_usr
import uid_name
from draw_pb2 import *
from draw_common import *
from draw_user_mgr import *
from mode import *
from datetime import datetime

import time
import logging
import draw_logging

class DrawRuntimeData(object):
    def __init__(self, draw_channel):
        self._draw_actions = []
        self._draw_channel = draw_channel
        self._chat_interval = 2
        self._channel_dictionary_rate = CHANNEL_DICTIONARY_RATE_LOW
        self._ban_list = []
    
    def GetChannelDictionaryRate(self):
        return self._channel_dictionary_rate
        
    def SetChannelDictionaryRate(self, new_rate):
        self._channel_dictionary_rate = new_rate 
    
    def SetChatInterval(self, interval):
        self._chat_interval = interval
        
    def GetChatInterval(self):
        return self._chat_interval
        
    def AddDrawAction(self, action):
        if len(self._draw_actions) > DrawConfig.MAX_DRAW_ACTIONS_AMOUNT:
            self._draw_actions.pop(0)
        
        self._draw_actions.append(action)
        
    def ClearDrawAction(self):
        self._draw_actions = []
        
    def GetDrawActions(self):
        return self._draw_actions
        
    def GetChatConfig(self):
        if CONFIG_BAN_ALL in self._ban_list:
            return CHAT_CONFIG_BAN_ALL
        elif CONFIG_BAN_WATCHER in self._ban_list:
            return CHAT_CONFIG_BAN_WATCHER_ONLY
        else:
            return CHAT_CONFIG_RELEASE_ALL
    
    def SetChatConfig(self,chat_config):
        #聊天模式的变化不会修改个人禁言设定
        #聊天模式是互斥的状态变化
        if chat_config == CHAT_CONFIG_RELEASE_ALL:
            if CONFIG_BAN_ALL in self._ban_list:
                self._ban_list.remove(CONFIG_BAN_ALL)
            if CONFIG_BAN_WATCHER in self._ban_list:
                self._ban_list.remove(CONFIG_BAN_WATCHER)
        elif chat_config == CHAT_CONFIG_BAN_ALL:
            if CONFIG_BAN_ALL not in self._ban_list:
                self._ban_list.append(CONFIG_BAN_ALL)
            if CONFIG_BAN_WATCHER in self._ban_list:
                self._ban_list.remove(CONFIG_BAN_WATCHER)
        elif chat_config == CHAT_CONFIG_BAN_WATCHER_ONLY:
            if CONFIG_BAN_ALL in self._ban_list:
                self._ban_list.remove(CONFIG_BAN_ALL)
            if CONFIG_BAN_WATCHER not in self._ban_list:
                self._ban_list.append(CONFIG_BAN_WATCHER)
        
    def AddBanTarget(self, target):
        if target not in self._ban_list:
            self._ban_list.append(target)
        
    def IfBanTarget(self, target):
        #print "IfBanTarget._ban_list = "
        #print self._ban_list
        if CONFIG_BAN_ALL in self._ban_list:
            return True
        if target in self._ban_list:
            return True
        return False
    
    def ReleaseBanTarget(self, target):
        if target == CONFIG_RELEASE_ALL:
            self.ClearBanlist()
        elif target in self._ban_list:
            self._ban_list.remove(target)
    
    def ClearBanlist(self):
        self._ban_list = []
        
class DrawChannel(object):
    def __init__(self, topchannel_id, yysubchannel_id):
        self._channel_id = yysubchannel_id
        self._topchannel_id = topchannel_id
        self._user_dict = {}
        self._watcher_dict = {}
        self._userid_list = []
        self._runtime_data = DrawRuntimeData(self)
        self._score_mgr = ChannelScoreMgr(self)
        self._master_id = 0
        self._next_master_id = 0
        self._last_master_id = 0
        self._logger = logging.getLogger(draw_logging.LOGIC_DEBUG_LOG)
        self._round_logger = logging.getLogger(draw_logging.DRAW_ROUND_LOG)
        self._last_check_time = 0
        
        self._mode_contrainer = { STANDRAD_TURN:StandradMode(self), PRESIDING_TURN:PresidingMode(self), ALTERNATION_TURN:AlternationMode(self), }
        self._cur_mode = STANDRAD_TURN
        self.GetCurMode().ModeRefresh()
        
        uid_name.GetShortChannelIdMgr().NewTopChannel(topchannel_id)
        from draw_main import *
        GetDrawMainMgr().SendPYYSessionGetYYChannelInfoRequest(topchannel_id)
    
    def StartActionRequest(self, uid,dc2ds_start_action_request_obj):
        res = ds2dc_start_action_response()
        res.end_time = int(time.time()) + dc2ds_start_action_request_obj.duration*60
        
        from authority import *
        from chl_usr import *
        role = GetAllUsrChlRoleMgr().GetUsrChlRole(uid, self._channel_id)
        if not GetAuthorityMgr().GetMasterTypeAuthority(role):
            res.set_response = res.FAIL_ERROR_OP_AUTHORITY
        elif dc2ds_start_action_request_obj.duration > DrawConfig.MAX_ACTION_DURATION:
            res.response_type = res.FAIL_DURATION_ERROR
        elif self._score_mgr.GetStatus():
            res.response_type = res.FAIL_STARTED_ALREADY
        else:
            res.response_type = res.OK
        GetDrawUserMgr().SendMessage(uid, self._topchannel_id, res)
        
        if res.response_type == res.OK:
            self._score_mgr.Start(uid,dc2ds_start_action_request_obj.duration*60)
    
    def StopActionRequest(self, uid,dc2ds_stop_action_request_obj):
        res = ds2dc_stop_action_response()
        
        from authority import *
        from chl_usr import *
        role = GetAllUsrChlRoleMgr().GetUsrChlRole(uid, self._channel_id)
        if not GetAuthorityMgr().GetMasterTypeAuthority(role):
            res.set_response = res.FAIL_ERROR_OP_AUTHORITY
        elif not self._score_mgr.GetStatus():
            res.response_type = res.FAIL_STOPED_ALREADY
        else:
            res.response_type = res.OK
        GetDrawUserMgr().SendMessage(uid, self._topchannel_id, res)
        
        if res.response_type == res.OK:
            self._score_mgr.Stop(uid)
    
    def UseItemRequest( self, uid, dc2ds_use_item_request_obj):           
        if self.CheckUser(uid):
            user = GetDrawUserMgr().GetUserByUid(uid)
            
            _target_uid = 0
            if dc2ds_use_item_request_obj.target_type == TARGET_MASTER_DRAWER:
                _target_uid = self.GetMasterDrawId()
                if _target_uid == 0:
                    _target_uid = self._last_master_id
            elif dc2ds_use_item_request_obj.target_type == TARGET_SELF:
                _target_uid = uid
            elif dc2ds_use_item_request_obj.target_type == TARGET_UID:
                if dc2ds_use_item_request_obj.HasField('target_uid'):
                    _target_uid = dc2ds_use_item_request_obj.target_uid
            
            print "UseItemRequest uid=[%d] target_uid=[%d] item_type=[%d] amount=[%d]" % (uid,_target_uid,dc2ds_use_item_request_obj.item_type,dc2ds_use_item_request_obj.amount)
            
            target_user = GetDrawUserMgr().GetUserByUid(_target_uid)
            if user is not None and target_user is not None:
                res = ds2dc_use_item_response()
                res.target_uid = _target_uid
                res.item_type = dc2ds_use_item_request_obj.item_type
                res.amount = dc2ds_use_item_request_obj.amount
                
                if _target_uid == uid:
                    res.response_type = res.FAIL_THIS_ITEM_CAN_NOT_USE_ON_SELF
                elif dc2ds_use_item_request_obj.target_type != TARGET_MASTER_DRAWER:
                    res.response_type = res.FAIL_ERROR_TARGET
                elif self.GetCurMode().GetCurStateId() != ESTIMATE_STATE:
                    res.response_type = res.FAIL_ERROR_STATE
                elif not user.ChangeObjAmount(dc2ds_use_item_request_obj.item_type,0-dc2ds_use_item_request_obj.amount):
                    res.response_type = res.FAIL_ERROR_NOT_ENOUGTH_AMOUNT
                else:
                    res.response_type = res.OK
                    
                    if dc2ds_use_item_request_obj.item_type == OBJ_CATEGORY_FLOWER:
                        target_user.GetUserScore().ReceiveGoodItem(dc2ds_use_item_request_obj.amount)
                        self._score_mgr.ReceiveGoodItem(_target_uid,dc2ds_use_item_request_obj.amount)
                    else:
                        target_user.GetUserScore().ReceiveBadItem(dc2ds_use_item_request_obj.amount)
                        self._score_mgr.ReceiveBadItem(_target_uid,dc2ds_use_item_request_obj.amount)
                    
                    #通知房间内其他人
                    res_notification = ds2dc_use_item_notification()
                    res_notification.uid = uid
                    res_notification.target_uid = _target_uid
                    res_notification.item_type = dc2ds_use_item_request_obj.item_type
                    res_notification.amount = dc2ds_use_item_request_obj.amount
                    self.SendMsgToDrawChannelUsrs(uid,res_notification)
                    
                user.SendMessage(self._topchannel_id , res)

    def CheckEventTime(self):
        if self._topchannel_id == DrawEventConfig.EVENT_CHANNEL:
            now_time = datetime.now()
            if now_time.day == DrawEventConfig.EVENT_DAY:
                if now_time.hour >= DrawEventConfig.EVENT_BEGIN_HOUR:
                    if now_time.month == DrawEventConfig.EVENT_MONTH:
                        if now_time.year == DrawEventConfig.EVENT_YEAR:
                            return True
        return False
                
    def SendPreDrawActions(self,uid):
        if not self.CheckEventTime():
            all_draw_actions = self._runtime_data.GetDrawActions()
            new_draw = ds2dc_draw_action()
            for one_draw_action in all_draw_actions:
                new_draw.draw_action = one_draw_action.draw_action
                GetDrawUserMgr().SendMessage(uid, self._topchannel_id, new_draw)
      
    def MasterDoDraw(self, uid, dc2ds_master_draw_action_obj):        
        new_draw = ds2dc_draw_action()
        new_draw.draw_action = dc2ds_master_draw_action_obj.draw_action
        self.SendMsgToDrawChannelUsrs( uid, new_draw )
        
        self._runtime_data.AddDrawAction( new_draw )
      
    def UserApply(self,uid):
        print "DrawChannel %d UserApply = %d" % (self._channel_id, uid)
        if self.GetCurMode().GetGameModeId() == STANDRAD_TURN and self.GetCurMode().GetCurStateId() == APPLY_STATE:
            self.GetCurMode().GetCurState().UserApply(uid)
      
    def GetUserAmount(self):
        return len(self._user_dict)
        
    def GetWatcherAmount(self):
        return len(self._watcher_dict)
        
    def ClearChannelRoundScore(self):
        for user in self._user_dict.values():
            user.GetUserScore().ClearRoundScore()
            self._score_mgr.ClearRoundScore(user._uid)
        for watcher in self._watcher_dict.values():
            watcher.GetUserScore().ClearRoundScore()
            self._score_mgr.ClearRoundScore(watcher._uid)
    
    def StandardGameStateStop(self):

        for user in self._user_dict.values():
            if user._uid == self.GetMasterDrawId():
                user.GetUserScore().OneRound(True)
                self._score_mgr.OneRound(user._uid,True)
            else:
                user.GetUserScore().OneRound(False)
                self._score_mgr.OneRound(user._uid,False)
        for watcher in self._watcher_dict.values():
            watcher.GetUserScore().OneRound(False)
            self._score_mgr.OneRound(watcher._uid,False)
            
        self._last_master_id = self._master_id
        simulate_request = dc2ds_change_role_request()
        simulate_request.target_uid = self.GetMasterDrawId()
        simulate_request.role_type = WATCHER_ROLE
        self.DoChangeRole(0, simulate_request)
    
    def ChannelMasterDrawScoreUpdate(self,uid):
        print "ChannelMasterDrawScoreUpdate uid=%d topchannel=%d channel_id=%d" % (uid, self._topchannel_id, self._channel_id)
        master_draw_res = dc2ds_get_score_request()
        master_draw_res.target_type = TARGET_MASTER_DRAWER
    
        from draw_main import *
        
        if uid != 0:
            GetDrawMainMgr().Ondc2ds_get_score_request(uid, self._topchannel_id, self._channel_id, master_draw_res)
        else:
            for user in self._user_dict.values():
                GetDrawMainMgr().Ondc2ds_get_score_request(user._uid, self._topchannel_id, self._channel_id, master_draw_res)
            for watcher in self._watcher_dict.values():
                GetDrawMainMgr().Ondc2ds_get_score_request(watcher._uid, self._topchannel_id, self._channel_id, master_draw_res)
    
    def ChannelUsrsScoreUpdate(self):
        self_res = dc2ds_get_score_request()
        self_res.target_type = TARGET_SELF

        from draw_main import *
        for user in self._user_dict.values():
            GetDrawMainMgr().Ondc2ds_get_score_request(user._uid, self._topchannel_id, self._channel_id, self_res)
        for watcher in self._watcher_dict.values():
            GetDrawMainMgr().Ondc2ds_get_score_request(watcher._uid, self._topchannel_id, self._channel_id, self_res)        
    
    def StandardGameStateStart(self):
        if self.GetCurMode().GetGameModeId() == STANDRAD_TURN and self.GetCurMode().GetCurStateId() == GAME_STATE:
            all_apply_list = self.GetCurMode().GetSpecState(APPLY_STATE).GetApplyList()
            max_roll = 0
            max_roll_uid = 0
            
            for apply_uid in all_apply_list.keys():
                #参与了roll点，开始游戏时候不在线的用户被视作弃权
                if apply_uid in self._watcher_dict:
                    if all_apply_list[apply_uid] >= max_roll:
                        max_roll = all_apply_list[apply_uid]
                        max_roll_uid = apply_uid
                     
            if max_roll_uid != 0:
                res = ds2dc_game_state()
                res.drawer_id = max_roll_uid
                res.round_second = DrawStateConfig.GAME_STATE_DURATION_SEC
                #self.SendMsgToDrawChannelUsrs( max_roll_uid, res )
                res.key_word = self.GetCurMode().GetCurState().GetKeyWord()._word_str
                #GetDrawUserMgr().SendMessage(max_roll_uid, self._topchannel_id, res )
                self.SendMsgToDrawChannelUsrs( 0, res )
                
                #通知频道把主笔玩家提到 PLAYER_ROLE
                simulate_request = dc2ds_change_role_request()
                simulate_request.target_uid = max_roll_uid
                simulate_request.role_type = PLAYER_ROLE
                self.DoChangeRole(max_roll_uid, simulate_request)
                
                self.DoSetMasterDrawId(max_roll_uid)
                self.ClearChannelRoundScore()
                self._runtime_data.ClearDrawAction()
                
                chat_notification_res = ds2dc_chat_notification()
                chat_notification_res.from_uid = 0
                chat_notification_res.chat_mode = SYSTEM_CHAT
                full_msg = '本轮共%d位用户报名，%s 投出最高 %d 点，为本回合主笔！' % (len(all_apply_list), uid_name.GetUidNameMgr().GetUserName(max_roll_uid).encode('utf-8'), all_apply_list[max_roll_uid])
                chat_notification_res.chat_msg = full_msg.decode('utf-8')
                self.SendMsgToDrawChannelUsrs(0, chat_notification_res)
                                
                self.ChannelMasterDrawScoreUpdate(0)
                                
                from datetime import date
                weeknum = date.today().isocalendar()[1]
                self._round_logger.info("week[%d] StandardGameStateStart chn=[%d] topchn=[%d] mode=[%d] masterid=[%d] player[%d] watcher[%d] apply_amount=[%d] max_apply=[%d]" % (weeknum, self._channel_id, self._topchannel_id, self.GetCurMode().GetGameModeId(), self._master_id, len(self._user_dict), len(self._watcher_dict), len(all_apply_list), all_apply_list[max_roll_uid] ))
                return True
                
        return False
            
    def AddChnUserScore(self, uid):
        if self._score_mgr.GetStatus():
            chn_user_score = self._score_mgr.GetAUser(uid)
            if chn_user_score is None:
                chn_user_score = self._score_mgr.AddAUser(uid)
            
            self._score_mgr.UserEnterChnScoreNotification(uid)
    
    def StandardEstimateStateStart(self):
        if self.GetCurMode().GetGameModeId() == STANDRAD_TURN and self.GetCurMode().GetCurStateId() == ESTIMATE_STATE:            
            if self._score_mgr.GetStatus():
                self._score_mgr.SendChnScoreNotification(0)

            res = ds2dc_estimate_state()
            res.last_drawer_id = self._last_master_id
            keyword = self.GetCurMode().GetSpecState(GAME_STATE).GetKeyWord()
            res.last_keyword = self.GetCurMode().GetSpecState(GAME_STATE).GetKeyWord().str()
            res.state_second = DrawStateConfig.ESTIMATE_STATE_DURATION_SEC

            if not keyword.IsSystemWord():
                res.word_commit_uid = keyword._word_commit_uid
                res.word_commit_name = keyword._word_commit_name
                draw_channel = GetDrawChannelMgr().GetDrawChannelByChannelId( keyword._word_commit_channel )
                if draw_channel is None:
                    res.word_commit_channel = uid_name.GetShortChannelIdMgr().GetShortChannelId(keyword._word_commit_channel)
                else:
                    res.word_commit_channel = uid_name.GetShortChannelIdMgr().GetShortChannelId(draw_channel._topchannel_id)

            for user in self._user_dict.values():
                res.flower_amount = user._bag.GetObjAmount(OBJ_CATEGORY_FLOWER)
                res.egg_amount = user._bag.GetObjAmount(OBJ_CATEGORY_EGG)
                user.SendMessage(self._topchannel_id , res)
            for watcher in self._watcher_dict.values():
                res.flower_amount = watcher._bag.GetObjAmount(OBJ_CATEGORY_FLOWER)
                res.egg_amount = watcher._bag.GetObjAmount(OBJ_CATEGORY_EGG)
                watcher.SendMessage(self._topchannel_id , res)
            return True
            
        return False

    def StandardApplyStateStart(self):
        if self.GetCurMode().GetGameModeId() == STANDRAD_TURN and self.GetCurMode().GetCurStateId() == APPLY_STATE:
            for uid in self._user_dict.keys():
                simulate_request = dc2ds_change_role_request()
                simulate_request.target_uid = uid
                simulate_request.role_type = WATCHER_ROLE
                self.DoChangeRole(0, simulate_request)
                
            res = ds2dc_apply_state()
            res.state_second = DrawStateConfig.APPLY_STATE_DURATION_SEC
            res.apply_amount = DrawStateConfig.APPLY_MAX_AMOUNT
            self.SendMsgToDrawChannelUsrs( 0, res )
            
            self.ChannelUsrsScoreUpdate()
            return True
            
        return False
        
    def AlternationEstimateStateStart(self):
        pass
        
    def AlternationGameStateStart(self):
        pass
        
    def PresidingDrawStateStart(self):
        pass
        
    def GetCurMode(self):
        return self._mode_contrainer.get(self._cur_mode)

    def DoChangeRole(self, uid, dc2ds_change_role_request):
        if dc2ds_change_role_request.role_type == PLAYER_ROLE or dc2ds_change_role_request.role_type == DRAWING_ROLE:
            remove_dict = self._watcher_dict
            add_dict = self._user_dict
        elif dc2ds_change_role_request.role_type == WATCHER_ROLE:
            remove_dict = self._user_dict
            add_dict = self._watcher_dict
        
        if remove_dict.has_key(dc2ds_change_role_request.target_uid):
            notification_res = ds2dc_change_role_notification()
            notification_res.operation_uid = uid
            notification_res.target_uid_list.append(dc2ds_change_role_request.target_uid)
            notification_res.role_type = dc2ds_change_role_request.role_type
            self.SendMsgToDrawChannelUsrs( uid, notification_res)
        
            user = remove_dict.pop(dc2ds_change_role_request.target_uid)
            add_dict[dc2ds_change_role_request.target_uid] = user
            if dc2ds_change_role_request.role_type == PLAYER_ROLE or dc2ds_change_role_request.role_type == DRAWING_ROLE:
                if dc2ds_change_role_request.target_uid not in self._userid_list:
                    self._userid_list.append(dc2ds_change_role_request.target_uid)
                elif self.GetCurMode().GetGameModeId() == ALTERNATION_TURN:
                    self.StoreNextMasterDrawId( self._master_id )
            else:
                if dc2ds_change_role_request.target_uid in self._userid_list:
                    self._userid_list.remove(dc2ds_change_role_request.target_uid)
                if self._master_id == dc2ds_change_role_request.target_uid:
                    self.SetMasterDrawId(0)
                    
        if self.GetCurMode().GetGameModeId() == PRESIDING_TURN and dc2ds_change_role_request.role_type == DRAWING_ROLE: 
            self.SetMasterDrawId(dc2ds_change_role_request.target_uid)
            
    def CheckAuthority(self, uid, yychannel_id):
        from authority import *
        role = chl_usr.GetAllUsrChlRoleMgr().GetUsrChlRole(uid, yychannel_id)
        return GetAuthorityMgr().GetMasterTypeAuthority(role)
            
    def ChangeRole(self, uid, dc2ds_change_role_request):
        res = ds2dc_change_role_response()
        res.target_uid = dc2ds_change_role_request.target_uid
        res.role_type = dc2ds_change_role_request.role_type
        res.change_response = res.OK

        if dc2ds_change_role_request.role_type == DRAWING_ROLE and self.GetCurMode().GetGameModeId() != PRESIDING_TURN:
            res.change_response = res.FAIL_ERROR_TURN
        else:
            if not self.CheckAuthority(uid, self._channel_id):
                if self.GetCurMode().GetGameModeId() == PRESIDING_TURN:
                    if uid == dc2ds_change_role_request.target_uid:
                        res.change_response = res.FAIL_ERROR_TURN
                    else:
                        res.change_response = res.FAIL_ERROR_OP_AUTHORITY
                elif self.GetCurMode().GetGameModeId() == ALTERNATION_TURN:
                    if uid != dc2ds_change_role_request.target_uid:
                        res.change_response = res.FAIL_ERROR_OP_AUTHORITY

            if dc2ds_change_role_request.role_type == PLAYER_ROLE:
                if self._user_dict.has_key(dc2ds_change_role_request.target_uid):
                    res.change_response = res.FAIL_BE_THE_ROLE_ALREADY
            if dc2ds_change_role_request.role_type == PLAYER_ROLE or dc2ds_change_role_request.role_type == DRAWING_ROLE :
                if len(self._user_dict) > DrawConfig.MAXPLAYER:
                    res.change_response = FAIL_PLAYER_FULL
            elif dc2ds_change_role_request.role_type == WATCHER_ROLE:
                if self._watcher_dict.has_key(dc2ds_change_role_request.target_uid):
                    res.change_response = res.FAIL_BE_THE_ROLE_ALREADY
                
        GetDrawUserMgr().SendMessage(uid, self._topchannel_id, res )
        
        if res.change_response == res.OK:
            self.DoChangeRole(uid, dc2ds_change_role_request)
            
    def CanMasterDraw(self,uid):
        if self.GetCurMode().GetGameModeId() == ALTERNATION_TURN:
            if self.GetCurMode().GetCurStateId() != ALTERNATION_GAME_STATE:
                return False
        if self._master_id != uid:
            return False
        if not self._user_dict.has_key(uid):
            return False
        return True
    
    def DoClearArena(self):
        res = ds2dc_change_role_notification()
        res.operation_uid = 0
        res.role_type = WATCHER_ROLE
        for user in self._user_dict.values():
            res.target_uid_list.append(user._uid)
            self._watcher_dict[user._uid] = user
            
        self.SendMsgToDrawChannelUsrs( 0, res)
            
        self._user_dict = {}
        self._userid_list = []
        
        self.SetMasterDrawId(0)
    
    def DoSetMasterType(self, uid, dc2ds_set_master_type_request):
        #self.GetCurMode().GetGameModeId() = dc2ds_set_master_type_request.master_type
        self.GetCurMode().ModeStop()
        self._cur_mode = dc2ds_set_master_type_request.master_type
        self.GetCurMode().ModeRefresh()
        
        #设置新模式成功，通知频道内其他用户
        channel_usr_res = ds2dc_set_master_type_notification()
        channel_usr_res.operation_uid = uid
        channel_usr_res.master_type = dc2ds_set_master_type_request.master_type
        channel_usr_res.drawer_id = 0
        
        if self.GetCurMode().GetGameModeId() == PRESIDING_TURN:    #主持模式
            channel_usr_res.second = DrawConfig.ROUND_PRESIDING_DURATION_SECOND
            self._logger.info("Set PRESIDING_TURN Channel=[%d] TopChannel=[%d] MasterDrawId=[%d] Player[%d] Watcher[%d]" % (self._channel_id, self._topchannel_id, self._master_id, len(self._user_dict), len(self._watcher_dict) ))
        elif self.GetCurMode().GetGameModeId() == ALTERNATION_TURN:    #轮流模式:
        #    self.StoreNextMasterDrawId(uid)
            channel_usr_res.second = DrawConfig.ROUND_DURATION_SECOND
            self._logger.info("Set ALTERNATION_TURN Channel=[%d] TopChannel=[%d] MasterDrawId=[%d] Player[%d] Watcher[%d]" % (self._channel_id, self._topchannel_id, self._master_id, len(self._user_dict), len(self._watcher_dict) ))
        else:
            channel_usr_res.second = 0
            self._logger.info("Set STANDRAD_TURN Channel=[%d] TopChannel=[%d] MasterDrawId=[%d] Player[%d] Watcher[%d]" % (self._channel_id, self._topchannel_id, self._master_id, len(self._user_dict), len(self._watcher_dict) ))
    
        self.SendMsgToDrawChannelUsrs( uid, channel_usr_res)
        
        self.DoClearArena()
    
    def SetMasterType(self,uid,dc2ds_set_master_type_request):
        user = GetDrawUserMgr().GetUserByUid(uid)
        if user is not None:
            res = ds2dc_set_master_type_response()
            res.master_type = dc2ds_set_master_type_request.master_type
            res.drawer_id = dc2ds_set_master_type_request.drawer_id #need_remove
            res.second = dc2ds_set_master_type_request.second       #need_remove
            
            if dc2ds_set_master_type_request.master_type == self.GetCurMode().GetGameModeId():
                res.set_response = res.FAIL_BE_THE_MASTER_TYPE_ALREADY
            else:
                from authority import *
                from chl_usr import *
                role = GetAllUsrChlRoleMgr().GetUsrChlRole(uid, self._channel_id)
                if not GetAuthorityMgr().GetMasterTypeAuthority(role):
                    res.set_response = res.FAIL_ERROR_OP_AUTHORITY
                else:
                    res.set_response = res.OK
                    self.DoSetMasterType(uid,dc2ds_set_master_type_request)

            #把设置新模式的结果(成功或者失败)返回给设置者
            user.SendMessage(self._topchannel_id , res)
            
    def GetMasterDrawId(self):
        return self._master_id
               
    def DoSetMasterDrawId(self, master_id):
        if self._master_id != master_id:
            self._master_id = master_id 
            
            if self._master_id > 0:
                self.StoreNextMasterDrawId(master_id)
        
    def SetMasterDrawId(self, master_id):
        self.DoSetMasterDrawId(master_id)
    
        set_res = ds2dc_set_master_drawer()
        set_res.drawer_id = master_id
        
        if self.GetCurMode().GetGameModeId() == ALTERNATION_TURN:
            if master_id > 0:
                set_res.round_second = DrawConfig.ROUND_DURATION_SECOND
            else:
                set_res.round_second = DrawConfig.ROUND_INTERVAL_SECOND
        else:
            set_res.round_second = DrawConfig.ROUND_PRESIDING_DURATION_SECOND
            
        self.SendMsgToDrawChannelUsrs( 0, set_res )
        
    def StoreNextMasterDrawId(self, master_id):
        user_amount = len(self._userid_list)
        if user_amount < 2:
            self._next_master_id = 0
        else:
            if master_id in self._userid_list:
                index = self._userid_list.index(master_id)
                if index +1 == user_amount:
                    self._next_master_id = self._userid_list[0]
                else:
                    self._next_master_id = self._userid_list[index +1]
            else:
                self._next_master_id = self._userid_list[0]
        
    def GetNextMasterDrawId(self):
        if self._next_master_id == 0:
            if len(self._userid_list) < 1:
                return 0
            else:
                return self._userid_list[0]
        return self._next_master_id
        
    def BeginRound(self,time):
        if len(self._user_dict) >= 1:
            next_master = self.GetNextMasterDrawId()
            if next_master != 0:
                from datetime import date
                weeknum = date.today().isocalendar()[1]
                self.SetMasterDrawId(next_master)
                self._round_logger.info("week[%d] BeginRound chn=[%d] topchn=[%d] time=[%d] mode=[%d] masterid=[%d] player[%d] watcher[%d]" % (weeknum, self._channel_id, self._topchannel_id, time, self.GetCurMode().GetGameModeId(), self._master_id, len(self._user_dict), len(self._watcher_dict) ))
        
    def EndRound(self,time):
        from datetime import date
        weeknum = date.today().isocalendar()[1]
        self._round_logger.info("week[%d] EndRound chn=[%d] topchn=[%d] time=[%d] mode=[%d] masterid=[%d] player[%d] watcher[%d]" % (weeknum, self._channel_id, self._topchannel_id, time, self.GetCurMode().GetGameModeId(), self._master_id, len(self._user_dict), len(self._watcher_dict) ))
        if self.GetCurMode().GetGameModeId() == ALTERNATION_TURN:
            self.SetMasterDrawId(0)
     
    def ClearZombieUsers(self):
        for uid in self._user_dict.keys():
            if self._user_dict[uid] is None:
                del self._user_dict[uid]
        for wuid in self._watcher_dict.keys():
            if self._watcher_dict[wuid] is None:
                del self._watcher_dict[wuid]
     
    def OnTimer(self,timer_time,stand_time):
        self.GetCurMode().GetCurState().OnTimer(timer_time)
        
        self._score_mgr.ActionOnTimer(stand_time)
        
        if self._last_check_time == 0:
            self._last_check_time = timer_time
        if timer_time - self._last_check_time >= DrawConfig.MAX_PING_IDLE_TIME:
            self._last_check_time = timer_time
            self.ClearZombieUsers()
            
            self._logger.info("channel idle check Channel=[%d]" % (self._channel_id))
            remove_list = []
            for user in self._user_dict.values():
                last_channel = user.GetUserLastChannel()
                if last_channel is not None and last_channel._channel_id != self._channel_id:
                    remove_list.append(user._uid)
                elif not user.GetOnlineFlag():
                    remove_list.append(user._uid)
            for watcher in self._watcher_dict.values():
                last_channel = watcher.GetUserLastChannel()
                if last_channel is not None and last_channel._channel_id != self._channel_id:
                    remove_list.append(watcher._uid)
                elif not watcher.GetOnlineFlag():
                    remove_list.append(watcher._uid)
            for each_uid in remove_list:
                self._logger.info("kick channel idle user Channel=[%d] LastChannel=[%d] uid=[%d]" % (self._channel_id, last_channel._channel_id, each_uid))
                self.RemoveUser(each_uid)
        
    def CanAddUser(self, user):
        if not user.GetUserWatchFlag():  #玩家
            if len(self._user_dict) >= DrawConfig.MAXPLAYER:
                return False
        else:
            if len(self._watcher_dict) >= DrawConfig.MAXWATCHER:
                return False
        return True
           
    def SendModeStateInfo(self,uid):
        self.ChannelMasterDrawScoreUpdate(uid)
           
    def AddUser(self, user):
        last_channel = user.GetUserLastChannel()
        if last_channel is not None:
            last_channel.RemoveUser(user._uid)
    
        if not user.GetUserWatchFlag():  #玩家
            effect_dict = self._user_dict
            check_dict = self._watcher_dict
        else:
            effect_dict = self._watcher_dict
            check_dict = self._user_dict
    
        if not effect_dict.has_key(user._uid):
            effect_dict[user._uid] = user
            
            if not user.GetUserWatchFlag() and user._uid not in self._userid_list:
                self._userid_list.append(user._uid)
                                      
            #把新进入的用户资料发给频道原有用户
            new_user_res = ds2dc_add_drawer_list()
            new_user_res.amount = 1
            res_drawer = new_user_res.draw_member.add()
            res_drawer.uid = user._uid
            res_drawer.name = user.GetUserName()
            res_drawer.draw = False
            res_drawer.watch = user.GetUserWatchFlag()
            self.SendMsgToDrawChannelUsrs(user._uid, new_user_res)
            
            user.SetUserLastChannel(self)
            user.SetOnlineFlag(True)
        
            #容错：客户端异常退出
            if check_dict.has_key(user._uid):
                del check_dict[user._uid]
                                    
            #重放之前的画画动作
            self.SendPreDrawActions(user._uid)
            
            #补发回合信息，一般只是在一个回合的开始发送一次的
            self.SendModeStateInfo(user._uid)
            
            self.AddChnUserScore(user._uid)
                
    def RemoveUser(self, uid):
        user = GetDrawUserMgr().GetUserByUid(uid)
        if user is not None:
            user.SetOnlineFlag(False)
            
        if self._user_dict.has_key(uid):
            del self._user_dict[uid]
        if self._watcher_dict.has_key(uid):
            del self._watcher_dict[uid]
        if uid in self._userid_list:   #玩家
            self._userid_list.remove(uid)
                
        #把退出的用户资料发给频道原有用户
        remove_user_res = ds2dc_remove_drawer_list()
        remove_user_res.amount = 1
        remove_user_res.uid.append(uid)
        self.SendMsgToDrawChannelUsrs(uid, remove_user_res)
        
        #下一次的主笔用户离开游戏，找再下一位
        if self._next_master_id == uid:
            self.StoreNextMasterDrawId(uid)
            
        if self._master_id == uid:
            self.EndRound(0)
        
    def CheckChatPermition(self, uid):
        if self.CheckAuthority(uid, self._channel_id):
            return True
        elif self._runtime_data.IfBanTarget(CONFIG_BAN_ALL):
            return False
        elif self._runtime_data.IfBanTarget(CONFIG_BAN_WATCHER) and self._watcher_dict.has_key(uid):
           return False
        elif self._runtime_data.IfBanTarget(uid):
            return False
        return True
        
    def DoChat(self, uid, dc2ds_chat_request_obj):
        chat_notification_res = ds2dc_chat_notification()
        chat_notification_res.from_uid = uid
        chat_notification_res.chat_mode = dc2ds_chat_request_obj.chat_mode
        chat_notification_res.chat_msg = dc2ds_chat_request_obj.chat_msg
        send_to_oper = False
    
        if dc2ds_chat_request_obj.chat_mode == PRIVATE_CHAT:
            #私聊
            if dc2ds_chat_request_obj.HasField("target_uid"):
                chat_notification_res.target_uid = dc2ds_chat_request_obj.target_uid
                GetDrawUserMgr().SendMessage(dc2ds_chat_request_obj.target_uid, self._topchannel_id, chat_notification_res)
                GetDrawUserMgr().SendMessage(uid, self._topchannel_id, chat_notification_res)
        else:
            if dc2ds_chat_request_obj.chat_mode == CHAT_TO_ALL or dc2ds_chat_request_obj.chat_mode == CHAT_TO_PLAYER:
                for user_id in self._user_dict.keys():
                    GetDrawUserMgr().SendMessage(user_id, self._topchannel_id, chat_notification_res)
                    if user_id == uid:
                        send_to_oper = True
            if dc2ds_chat_request_obj.chat_mode == CHAT_TO_ALL or dc2ds_chat_request_obj.chat_mode == CHAT_TO_WATCHER:
                for watcher_id in self._watcher_dict.keys():
                    GetDrawUserMgr().SendMessage(watcher_id, self._topchannel_id, chat_notification_res)
                    if watcher_id == uid:
                        send_to_oper = True

            if not send_to_oper:
                GetDrawUserMgr().SendMessage(uid, self._topchannel_id, chat_notification_res)
                    
    def OnChat(self, uid,dc2ds_chat_request_obj):
        if self.GetCurMode().GetGameModeId() == STANDRAD_TURN and self.GetCurMode().GetCurStateId() == GAME_STATE:
            if self.GetCurMode().GetCurState().CheckKeyword(uid, dc2ds_chat_request_obj):
                #表示猜中答案了，不走普通聊天流程
                return
        
        chat_res = ds2dc_chat_response()
        chat_res.chat_mode = dc2ds_chat_request_obj.chat_mode
        
        if not self.CheckChatPermition(uid):
            chat_res.response_type = chat_res.FAIL_NOT_PERMIT_TO_CHAT
            GetDrawUserMgr().SendMessage(uid, self._topchannel_id, chat_res)
        else:
            self.DoChat(uid,dc2ds_chat_request_obj)
        
    def DoConfig(self, uid,dc2ds_config_request_obj):
        if dc2ds_config_request_obj.config_mode == CONFIG_SET_CHAT_INTERVAL:
           self._runtime_data.SetChatInterval(dc2ds_config_request_obj.chat_interval)
        elif dc2ds_config_request_obj.config_mode == CONFIG_BAN_ID:
            self._runtime_data.AddBanTarget(dc2ds_config_request_obj.target_uid)
        elif dc2ds_config_request_obj.config_mode in DrawConfig.BAN_OP:
            self._runtime_data.AddBanTarget(dc2ds_config_request_obj.config_mode)
        elif dc2ds_config_request_obj.config_mode == CONFIG_RELEASE_ID:
            self._runtime_data.ReleaseBanTarget(dc2ds_config_request_obj.target_uid)
        elif dc2ds_config_request_obj.config_mode in DrawConfig.RELEASE_OP:
            self._runtime_data.ReleaseBanTarget(dc2ds_config_request_obj.config_mode)
        elif dc2ds_config_request_obj.config_mode == CONFIG_SET_CHANNEL_DICTIONARY_RATE:
            self._runtime_data.SetChannelDictionaryRate(dc2ds_config_request_obj.channel_dictionary_rate)

        config_notification_res = ds2dc_config_notification()
        config_notification_res.op_uid = uid
        config_notification_res.config_mode = dc2ds_config_request_obj.config_mode
        if dc2ds_config_request_obj.HasField("target_uid"):
            config_notification_res.target_uid = dc2ds_config_request_obj.target_uid
        elif dc2ds_config_request_obj.HasField("chat_interval"):
            config_notification_res.chat_interval = dc2ds_config_request_obj.chat_interval
        elif dc2ds_config_request_obj.HasField("channel_dictionary_rate"):
            config_notification_res.channel_dictionary_rate = dc2ds_config_request_obj.channel_dictionary_rate
            
        self.SendMsgToDrawChannelUsrs(uid, config_notification_res)
        
    def OnConfig(self, uid,dc2ds_config_request_obj):
        response_res = ds2dc_config_response()
        response_res.config_mode = dc2ds_config_request_obj.config_mode
        response_res.config_response = response_res.OK
        if dc2ds_config_request_obj.HasField("target_uid"):
            response_res.target_uid = dc2ds_config_request_obj.target_uid
        elif dc2ds_config_request_obj.HasField("chat_interval"):
            response_res.chat_interval = dc2ds_config_request_obj.chat_interval
        elif dc2ds_config_request_obj.HasField("channel_dictionary_rate"):
            response_res.channel_dictionary_rate = dc2ds_config_request_obj.channel_dictionary_rate
        
        #必须要黄马或者以上才能进行设置
        if not self.CheckAuthority(uid, self._channel_id):
            response_res.config_response = response_res.FAIL_ERROR_OP_AUTHORITY
        else:
            if dc2ds_config_request_obj.config_mode in DrawConfig.BAN_OP and self._runtime_data.IfBanTarget(dc2ds_config_request_obj.config_mode):
                response_res.config_response = response_res.FAIL_TARGET_IS_BANNED
            elif dc2ds_config_request_obj.config_mode in DrawConfig.RELEASE_OP and not self._runtime_data.IfBanTarget(dc2ds_config_request_obj.config_mode):
                response_res.config_response = response_res.FAIL_TARGET_IS_NOT_BANNED
            elif dc2ds_config_request_obj.config_mode == CONFIG_SET_CHAT_INTERVAL:
                if dc2ds_config_request_obj.chat_interval < DrawConfig.CONFIG_MIN_CHAT_INTERVAL or dc2ds_config_request_obj.chat_interval > DrawConfig.CONFIG_MAX_CHAT_INTERVAL:
                    response_res.config_response = response_res.FAIL_INVALID_INTERVAL
                    
        if response_res.config_response == response_res.OK:
            self.DoConfig(uid,dc2ds_config_request_obj)
            
        GetDrawUserMgr().SendMessage(uid, self._topchannel_id, response_res)
      
    def DoChatConfig(self,uid,dc2ds_chat_config_request_obj):
        self._runtime_data.SetChatConfig(dc2ds_chat_config_request_obj.config_mode)
    
        notification_res = ds2dc_chat_config_notification()
        notification_res.op_uid = uid
        notification_res.config_mode = dc2ds_chat_config_request_obj.config_mode
        
        self.SendMsgToDrawChannelUsrs(uid, notification_res)
      
    def OnChatConfig(self,uid,dc2ds_chat_config_request_obj):
        response_res = ds2dc_chat_config_response()
        response_res.config_mode = dc2ds_chat_config_request_obj.config_mode
        response_res.config_response = response_res.OK
        
        #必须要黄马或者以上才能进行设置
        if not self.CheckAuthority(uid, self._channel_id):
            response_res.config_response = response_res.FAIL_ERROR_OP_AUTHORITY
        elif self._runtime_data.GetChatConfig() == dc2ds_chat_config_request_obj.config_mode:
            response_res.config_response = response_res.FAIL_BE_TARGET_ALREADY
        else:
            self.DoChatConfig(uid,dc2ds_chat_config_request_obj)
            
        GetDrawUserMgr().SendMessage(uid, self._topchannel_id, response_res)
        
    def SendMsgToDrawChannelUsrs(self, except_uid, msg):
        all_user_list = self._user_dict.keys() + self._watcher_dict.keys()
        from draw_main import *
        GetDrawMainMgr().SendGroupMessage(all_user_list,self._topchannel_id,msg)
        return
        
        for draw_user in self._user_dict.values():
            if draw_user._uid != except_uid:
                draw_user.SendMessage( self._topchannel_id, msg )
                
        for draw_user in self._watcher_dict.values():
            if draw_user._uid != except_uid:
                draw_user.SendMessage( self._topchannel_id, msg )
  
    def SendChannelUsersListToUser(self, user):
        #每个人进入画板都要重新组一次全频道画板用户数据，需要优化 to_do
        res = ds2dc_add_drawer_list()
        res.amount = len(self._user_dict) + len(self._watcher_dict)
        for draw_user in self._user_dict.values():                
            res_drawer = res.draw_member.add()
            res_drawer.uid = draw_user._uid
            res_drawer.name = draw_user.GetUserName()
            if self.GetMasterDrawId() == draw_user._uid:
                res_drawer.draw = True
            else:
                res_drawer.draw = False
            res_drawer.watch = False
                
        for draw_user in self._watcher_dict.values():
            res_drawer = res.draw_member.add()
            res_drawer.uid = draw_user._uid
            res_drawer.name = draw_user.GetUserName()
            res_drawer.draw = False
            res_drawer.watch = True
            
        user.SendMessage(self._topchannel_id, res)
      
    def CheckUser(self, uid):
        for draw_user_id in self._user_dict.keys():
            if uid == draw_user_id:
                return True
    
        for draw_watcher_id in self._watcher_dict.keys():
            if uid == draw_watcher_id:
                return True
    
        return False
    
class DrawChannelMgr(object):
    
    channels = {} # {yychannel_id:DrawChannel}
    channels_tree = {}

    def __init__(self):
        self._logger = logging.getLogger(draw_logging.LOGIC_DEBUG_LOG)
        self._round_logger = logging.getLogger(draw_logging.DRAW_ROUND_LOG)
       
    def UseItemRequest( self, uid, yychannel_id, yysubchannel_id, dc2ds_use_item_request_obj):
        draw_channel = self.GetDrawChannelByChannelId( yysubchannel_id )
        if draw_channel is not None:
            draw_channel.UseItemRequest( uid, dc2ds_use_item_request_obj)
       
    def CreateDrawChannel(self, yychannel_id, yysubchannel_id):
        topdraw_channel = self.GetDrawChannelByChannelId( yychannel_id )
        if topdraw_channel is None:
            topdraw_channel = DrawChannel(yychannel_id, yychannel_id)
            DrawChannelMgr.channels[yychannel_id] = topdraw_channel
            
        draw_channel = self.GetDrawChannelByChannelId( yysubchannel_id )
        if draw_channel is None:
            draw_channel = DrawChannel(yychannel_id, yysubchannel_id)
            DrawChannelMgr.channels[yysubchannel_id] = draw_channel

        if not DrawChannelMgr.channels_tree.has_key(yychannel_id):
            DrawChannelMgr.channels_tree[yychannel_id] = {}
            DrawChannelMgr.channels_tree[yychannel_id][yychannel_id] = topdraw_channel
            DrawChannelMgr.channels_tree[yychannel_id][yysubchannel_id] = draw_channel
        elif not DrawChannelMgr.channels_tree[yychannel_id].has_key(yysubchannel_id):
            DrawChannelMgr.channels_tree[yychannel_id][yysubchannel_id] = draw_channel
            
        return draw_channel
   
    def OnUserEnterLauncher(self, uid, yychannel_id, yysubchannel_id):    
        draw_channel = self.CreateDrawChannel( yychannel_id, yysubchannel_id )
        
        res = dc2ds_login_launcher_response()
        res.response = res.OK
        res.room_amount = 0
        res.topchannel_id = yychannel_id
        
        res.name = uid_name.GetUidNameMgr().GetUserName(uid)
        res.shortchannel_id = uid_name.GetShortChannelIdMgr().GetShortChannelId(yychannel_id)
        res.channel_name = uid_name.GetYYChannelidNameMgr().GetChannelName(yychannel_id)
        
        if DrawChannelMgr.channels_tree.has_key(yychannel_id):
            for subchannel in DrawChannelMgr.channels_tree[yychannel_id].values():
                total_user_amount = subchannel.GetUserAmount() + subchannel.GetWatcherAmount()
                if total_user_amount > 0:
                    res.room_amount = res.room_amount + 1
                    active_room = res.active_room_list.add()
                    active_room.room_type = INDIVIDUAL_CHANNEL_ROOM
                    active_room.room_name = uid_name.GetYYChannelidNameMgr().GetChannelName(subchannel._channel_id)
                    active_room.user_amount = total_user_amount
                    if subchannel._channel_id == yychannel_id:
                        active_room.show_only = False
                        active_room.room_id = 1
                    elif subchannel._channel_id == yysubchannel_id:
                        active_room.show_only = False
                        active_room.subchannel_id = yysubchannel_id
                    else:
                        active_room.show_only = True
        
        GetDrawUserMgr().SendMessage(uid, yychannel_id, res)
   
    def OnUserEnterDraw(self, uid, yychannel_id, yysubchannel_id, room_type, target_id ):
        user = GetDrawUserMgr().NewUser( uid )
        effect_channel_id = yysubchannel_id
        
        # 暂时还不支持直接登录非操作者所处的子频道，所以可以暂时忽略 target_id 
        if room_type == INDIVIDUAL_CHANNEL_ROOM:
            draw_channel = self.CreateDrawChannel( yychannel_id, yysubchannel_id )
        else:
            # 暂时不支持根频道大厅下多房间，所以可以暂时忽略 target_id 
            draw_channel = self.CreateDrawChannel( yychannel_id, yychannel_id )
            effect_channel_id = yychannel_id

        #发送登录返回信息给新用户
        res = ds2dc_login_response()
        res.response = res.OK
        res.uid = uid
        res.name = user.GetUserName()
        res.channel_id = yychannel_id       #不显示子频道id，统一发根频道id
        res.shortchannel_id = uid_name.GetShortChannelIdMgr().GetShortChannelId(yychannel_id)
        res.channel_name = uid_name.GetYYChannelidNameMgr().GetChannelName(effect_channel_id)
        res.channel_dictionary_rate = draw_channel._runtime_data.GetChannelDictionaryRate()
        if draw_channel._runtime_data.IfBanTarget(CONFIG_BAN_ALL):
            res.chat_config_mode = CHAT_CONFIG_BAN_ALL
        elif draw_channel._runtime_data.IfBanTarget(CONFIG_BAN_WATCHER):
            res.chat_config_mode = CHAT_CONFIG_BAN_WATCHER_ONLY
        else:
            res.chat_config_mode = CHAT_CONFIG_RELEASE_ALL
        res.chat_interval = draw_channel._runtime_data.GetChatInterval()
        if res.channel_name == "":
            from draw_main import *
            GetDrawMainMgr().SendPYYSessionGetYYChannelInfoRequest(yychannel_id)   #异步请求，第一个进入频道的用户无法拿到频道名
        res.master_type = draw_channel.GetCurMode().GetGameModeId()
        res.cur_state = draw_channel.GetCurMode().GetCurStateId()
        res.role_type = WATCHER_ROLE
        res.yyrole_type = chl_usr.GetAllUsrChlRoleMgr().GetUsrChlRole(uid, effect_channel_id)
            
        if not draw_channel.CanAddUser( user ):
            res.response = res.FAIL_SERVER_FULL
            user.SendMessage(yychannel_id, res)
        else:
            user.SendMessage(yychannel_id, res)
            draw_channel.AddUser( user )
            user.SetUserLocationFlag( room_type )
            #把频道原有用户资料发给新进入的用户
            draw_channel.SendChannelUsersListToUser(user)
            
            #add_flower_desc = ""
            #add_egg_desc = ""
            #if user.ChangeObjAmount(OBJ_CATEGORY_FLOWER,3):
            #    add_flower_desc = "ok"
            #else:
            #    add_flower_desc = "false"
            #if user.ChangeObjAmount(OBJ_CATEGORY_EGG,3):
            #    add_egg_desc = "ok"
            #else:
            #    add_egg_desc = "false"
            #self._logger.info("user login uid=[%d] flower=[%d] add_flower=%s egg=[%d] add_egg=%s" % (uid, user.GetObjAmount(OBJ_CATEGORY_FLOWER), add_flower_desc, user.GetObjAmount(OBJ_CATEGORY_EGG), add_egg_desc ) )
            self._logger.info("user login uid=[%d] flower=[%d] egg=[%d]" % (uid, user.GetObjAmount(OBJ_CATEGORY_FLOWER), user.GetObjAmount(OBJ_CATEGORY_EGG) ) )
            
            dc2ds_get_score_request_obj = dc2ds_get_score_request()
            dc2ds_get_score_request_obj.target_type = TARGET_SELF
            from draw_main import *
            GetDrawMainMgr().Ondc2ds_get_score_request(uid, yychannel_id, yysubchannel_id, dc2ds_get_score_request_obj)

    def UserLeaveYYChannel(self, uid, yychannel_id):
        draw_channel = self.GetDrawChannelByChannelId( yychannel_id )
        if draw_channel is not None:
            if draw_channel.GetMasterDrawId() == uid:
                draw_channel.SetMasterDrawId(0)
            draw_channel.RemoveUser( uid )
    
    #这里是发送到已经跳转后的新频道 yysubchannel_id
    def OnUserSubChannelChange(self, uid, yychannel_id, yysubchannel_id, last_channel_id):
        #print "OnUserSubChannelChange uid=%d, yychannel_id=%d, yysubchannel_id=%d" % (uid, yychannel_id, yysubchannel_id)
        user = GetDrawUserMgr().GetUserByUid(uid)
        if user is not None and user.GetUserLocationFlag() == INDIVIDUAL_CHANNEL_ROOM:
            res = ds2dc_quit_notification()
            #res.quit_type = res.SYSTEM_SUBCHANNEL_CHANGE
            res.quit_type = res.SYSTEM_MAINTENANCE
            user.SendMessage(yychannel_id, res)
            
            last_played_yychannel = user.GetUserLastChannel()
            if last_played_yychannel is not None:
                if last_played_yychannel.CheckUser(uid):
                    #表示用户跳转子频道的时候，在游戏中
                    self.UserLeaveYYChannel(uid, last_played_yychannel._channel_id)
                    
                    '''
                    跳转子频道会引发子频道房间有用户残影，先取消该功能。子频道跳转则立刻通知客户端关闭
                    #进入新频道
                    draw_channel = self.CreateDrawChannel( yychannel_id, yysubchannel_id )
                    
                    #发送换频道信息给用户
                    res = ds2dc_change_subchannel()
                    res.channel_id = yychannel_id
                    res.channel_name = uid_name.GetYYChannelidNameMgr().GetChannelName(yysubchannel_id)
                    if res.channel_name == "":
                        from draw_main import *
                        GetDrawMainMgr().SendPYYSessionGetYYChannelInfoRequest(yychannel_id)   #异步请求，第一个进入频道的用户无法拿到频道名
                    res.master_type = draw_channel.GetCurMode().GetGameModeId()
                    res.cur_state = draw_channel.GetCurMode().GetCurStateId()
                    res.role_type = WATCHER_ROLE
                    res.yyrole_type = chl_usr.GetAllUsrChlRoleMgr().GetUsrChlRole(uid, yychannel_id)
                    res.channel_dictionary_rate = draw_channel._runtime_data.GetChannelDictionaryRate()
                    if draw_channel._runtime_data.IfBanTarget(CONFIG_BAN_ALL):
                        res.chat_config_mode = CHAT_CONFIG_BAN_ALL
                    elif draw_channel._runtime_data.IfBanTarget(CONFIG_BAN_WATCHER):
                        res.chat_config_mode = CHAT_CONFIG_BAN_WATCHER_ONLY
                    else:
                        res.chat_config_mode = CHAT_CONFIG_RELEASE_ALL
                    res.chat_interval = draw_channel._runtime_data.GetChatInterval()
                    user.SendMessage(yychannel_id, res)
                    
                    if draw_channel.CanAddUser( user ):
                        user.SendMessage(yychannel_id, res)
                        draw_channel.AddUser( user )
                        #把频道原有用户资料发给新进入的用户
                        draw_channel.SendChannelUsersListToUser(user)
                    '''

    def OnUserLeaveDraw(self, uid, yychannel_id):
        #print "OnUserLeaveDraw uid=%d, yychannel_id=%d" % (uid, yychannel_id)
        self.UserLeaveYYChannel(uid, yychannel_id)
        GetDrawUserMgr().RemoveUser( uid )
        
    def OnSetMasterType(self, uid, yychannel_id, dc2ds_set_master_type_request):
        draw_channel = self.GetDrawChannelByChannelId( yychannel_id )
        if draw_channel is not None:
            draw_channel.SetMasterType(uid,dc2ds_set_master_type_request)
        
    def OnChangeRole(self, uid, yychannel_id, dc2ds_change_role_request):
        draw_channel = self.GetDrawChannelByChannelId( yychannel_id )
        if draw_channel is not None:
            draw_channel.ChangeRole(uid,dc2ds_change_role_request)
        
    def OnChatConfig(self, uid,yysubchannel_id,dc2ds_chat_config_request_obj):
        draw_channel = self.GetDrawChannelByChannelId( yysubchannel_id )
        if draw_channel is not None:
            draw_channel.OnChatConfig(uid,dc2ds_chat_config_request_obj)
        
    def OnChat(self, uid,yysubchannel_id,dc2ds_chat_request_obj):
        draw_channel = self.GetDrawChannelByChannelId( yysubchannel_id )
        if draw_channel is not None:
            draw_channel.OnChat(uid,dc2ds_chat_request_obj)
        
    def OnConfig(self, uid,yysubchannel_id,dc2ds_config_request_obj):
        draw_channel = self.GetDrawChannelByChannelId( yysubchannel_id )
        if draw_channel is not None:
            draw_channel.OnConfig(uid,dc2ds_config_request_obj)
    
    def OnTimer(self,timer_time):
        stand_time = int(time.time())
        for draw_channel in DrawChannelMgr.channels.values():
            draw_channel.OnTimer(timer_time,stand_time)
            
    def OnPreHalt(self):
        #to_do 还需要禁止用户登录，用状态记录，延时1分钟(一局游戏)处理比较好。
        res = ds2dc_quit_notification()
        res.quit_type = res.SYSTEM_REBOOT
        for draw_channel in DrawChannelMgr.channels.values():
            for user_id in draw_channel._user_dict.keys():
                self.OnUserLeaveDraw(user_id, draw_channel._channel_id)
            for watcher_id in draw_channel._watcher_dict.keys():
                self.OnUserLeaveDraw(watcher_id, draw_channel._channel_id)         
            draw_channel.SendMsgToDrawChannelUsrs( 0, res )
            
    def UserApply(self, uid, yysubchannel_id):
        draw_channel = self.GetDrawChannelByChannelId( yysubchannel_id )
        if draw_channel is not None:
            draw_channel.UserApply(uid)
            
    def GetDrawChannelByChannelId(self, yychannel_id):
        return DrawChannelMgr.channels.get(yychannel_id)
        
    def SendMsgToDrawChannelUsrs(self, except_uid, yychannel_id, msg):
        draw_channel = self.GetDrawChannelByChannelId( yychannel_id )
        if draw_channel is not None:
            draw_channel.SendMsgToDrawChannelUsrs( except_uid, msg )
            


            
g_dcmgr = None
def GetDrawChannelMgr():
    global g_dcmgr
    if g_dcmgr is None:
        g_dcmgr = DrawChannelMgr()
    return g_dcmgr

