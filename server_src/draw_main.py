# -*- coding:utf-8 -*-
'''
    file: draw_main.py
    author: xuzhijian
    date: 2011-06-28
    desc: 画板用户发来的交互信息

    广州华多网络科技有限公司 版权所有 (c) 2005-2010 DuoWan.com [多玩游戏]
'''
import DSFP
from c_python_interface import *
from dsf_protobuf_handle import *

import uid_name
from draw_channel_mgr import *
from draw_dictionary import *
from draw_user_mgr import *
from draw_dao import *

import draw_logging
import logging

from draw_pb2 import *
from draw_common import DrawConfig

class DrawMain(ConnectionHandle):
    def __init__(self):
        ConnectionHandle.__init__(self)
        self._login_logger = logging.getLogger(draw_logging.LOGIC_LOGIN_LOG)
        self._debug_logger = logging.getLogger(draw_logging.LOGIC_DEBUG_LOG)
        self._suggestion_logger = logging.getLogger(draw_logging.SUGGESTION_LOG)

    def RegisterMessage(self):
        self.AddHandler(dc2ds_login_request,                self.Ondc2ds_login_request)
        self.AddHandler(dc2ds_master_draw_action,           self.Ondc2ds_master_draw_action)
        self.AddHandler(dc2ds_logout_request,               self.Ondc2ds_logout_request)
        self.AddHandler(dc2ds_set_master_type_request,      self.Ondc2ds_set_master_type_request)
        self.AddHandler(dc2ds_change_role_request,          self.Ondc2ds_change_role_request)
        self.AddHandler(dc2ds_chat_request,                 self.Ondc2ds_chat_request)
        self.AddHandler(dc2ds_config_request,               self.Ondc2ds_config_request)
        self.AddHandler(dc2ds_chat_config_request,          self.Ondc2ds_chat_config_request)
        self.AddHandler(dc2ds_apply_drawer_request,         self.Ondc2ds_apply_drawer_request)
        self.AddHandler(dc2ds_ping,                         self.Ondc2ds_ping)
        self.AddHandler(dc2ds_manage_channel_words_request, self.Ondc2ds_manage_channel_words_request)
        self.AddHandler(dc2ds_update_channel_words_request, self.Ondc2ds_update_channel_words_request)
        self.AddHandler(dc2ds_submit_words_request,         self.Ondc2ds_submit_words_request)
        self.AddHandler(dc2ds_make_suggestions,             self.Ondc2ds_make_suggestions)
        self.AddHandler(dc2ds_login_launcher_request,       self.Ondc2ds_login_launcher_request)
        self.AddHandler(dc2ds_use_item_request,             self.Ondc2ds_use_item_request)
        self.AddHandler(dc2ds_get_score_request,            self.Ondc2ds_get_score_request)
        self.AddHandler(dc2ds_start_action_request,         self.Ondc2ds_start_action_request)
        self.AddHandler(dc2ds_stop_action_request,          self.Ondc2ds_stop_action_request)
        
    def Dispatch(self, uid, yychannel_id, yysubchannel_id, msg):
        self._debug_logger.info("Dispatch uid=%d yychannel_id=%d yysubchannel_id=%d uri=%d" % (uid, yychannel_id, yysubchannel_id, msg.GetUri()) )
        user = GetDrawUserMgr().GetUserByUid(uid)
        effect_channel_id = yysubchannel_id
        if user is not None:
            if user.GetOnlineFlag() and user.GetUserLocationFlag() != INDIVIDUAL_CHANNEL_ROOM:
                effect_channel_id = yychannel_id
        ConnectionHandle.Dispatch( self, uid, yychannel_id, effect_channel_id, msg )
        
    def SendPYYSessionGetYYChannelInfoRequest(self, yychannel_id):
        self._debug_logger.info("SendPYYSessionGetYYChannelInfoRequest = %d" % yychannel_id)
        DSFP.c_python_interface.PySendPYYSessionGetYYChannelInfoRequest(yychannel_id)
        
    def SendMessage(self, uid, yychannel_id, pb_ins):
        #self.transport.write(self._msgFactory.PackMessage(pb_ins))
        #DSFP.drawservice_module.PySendOriginalDataToChannel( yychannel_id, self._msgFactory.PackMessage(pb_ins))
        DSFP.c_python_interface.PySendOriginalDataToUser(uid, yychannel_id, self._msgFactory.PackMessage(pb_ins))
        
    def SendGroupMessage(self, uid_list, yychannel_id, pb_ins):
        uid_vec = Uint32Vector()
        for index in range(len(uid_list)-1):
            uid_vec.append(uid_list[index])
        DSFP.c_python_interface.PySendOriginalDataToUsers(uid_vec, yychannel_id, self._msgFactory.PackMessage(pb_ins))
        
    def PyGetAsidBySid(self, topchannel_id ):
        DSFP.c_python_interface.PyGetAsidBySid( str(topchannel_id) )

    def CheckClient(self, dc2ds_login_request_obj):
        if dc2ds_login_request_obj.main_version != DrawConfig.CLIENT_MAIN_VERSION:
            return False
        if dc2ds_login_request_obj.minor_version != DrawConfig.CLIENT_MINOR_VERSION:
            return False
            
        return True
        
    def SendStrMessage(self, uid, yychannel_id, str_data):
        #self.transport.write(self._msgFactory.PackMessage(pb_ins))
        #DSFP.drawservice_module.PySendOriginalDataToChannel( yychannel_id, self._msgFactory.PackMessage(pb_ins))
        DSFP.c_python_interface.PySendOriginalDataToUser(uid, yychannel_id, str_data)
        
        
    def Ondc2ds_login_request(self, uid, yychannel_id, yysubchannel_id, dc2ds_login_request_obj):
        if self.CheckClient(dc2ds_login_request_obj):
            from datetime import date
            weeknum = date.today().isocalendar()[1]
            self._login_logger.info("week[%d] Ondc2ds_login_request uid = %d, yychannel_id = %d, yysubchannel_id = %d, room_type = %d" % ( weeknum, uid, yychannel_id, yysubchannel_id, dc2ds_login_request_obj.room_type ))
            target_id = 0
            if dc2ds_login_request_obj.room_type == INDIVIDUAL_CHANNEL_ROOM:
                if dc2ds_login_request_obj.HasField("subchannel_id"):
                    target_id = dc2ds_login_request_obj.subchannel_id
            elif dc2ds_login_request_obj.room_type == UNIVERSAL_TOP_CHANNEL_HALL:
                if dc2ds_login_request_obj.HasField("room_id"):
                    target_id = dc2ds_login_request_obj.room_id
            GetDrawChannelMgr().OnUserEnterDraw(uid, yychannel_id, yysubchannel_id, dc2ds_login_request_obj.room_type, target_id )
        else:
            res = ds2dc_login_response()
            res.response = res.FAIL_INVALID_CLIENT_VERSION
            res.uid = uid
            res.name = ''
            res.channel_id = yysubchannel_id
            res.channel_name = ''
            res.master_type = STANDRAD_TURN
            res.role_type = WATCHER_ROLE
            res.yyrole_type = APP_YYCHANNEL_NORMAL_ROLE
            res.chat_interval = 3
            res.cur_state = APPLY_STATE
            res.chat_config_mode = CHAT_CONFIG_RELEASE_ALL
            res.channel_dictionary_rate = CHANNEL_DICTIONARY_RATE_LOW
            self.SendMessage(uid,yychannel_id,res)

    def Ondc2ds_master_draw_action(self, uid, yychannel_id, yysubchannel_id, dc2ds_master_draw_action_obj):
        #print "Ondc2ds_master_draw_action uid = %d, yychannel_id = %d, yysubchannel_id = %d" % ( uid, yychannel_id, yysubchannel_id )
        yychannel = GetDrawChannelMgr().GetDrawChannelByChannelId( yysubchannel_id )
        if yychannel is not None:
            if yychannel.CanMasterDraw(uid):
                yychannel.MasterDoDraw(uid,dc2ds_master_draw_action_obj)

    def Ondc2ds_logout_request(self, uid, yychannel_id, yysubchannel_id, dc2ds_logout_request):
        user = GetDrawUserMgr().GetUserByUid(uid)
        if user is not None:
            from datetime import date
            weeknum = date.today().isocalendar()[1]
            self._login_logger.info("week[%d] Ondc2ds_logout_request uid = %d, yychannel_id = %d, yysubchannel_id = %d" % ( weeknum, uid, yychannel_id, yysubchannel_id ))
            GetDrawDao().SaveUserScore(uid)
            GetDrawChannelMgr().OnUserLeaveDraw(uid,yysubchannel_id)

    def Ondc2ds_set_master_type_request(self, uid, yychannel_id, yysubchannel_id, dc2ds_set_master_type_request):
        self._debug_logger.info("Ondc2ds_set_master_type_request uid = %d, yychannel_id = %d, yysubchannel_id = %d" % ( uid, yychannel_id, yysubchannel_id ))
        GetDrawChannelMgr().OnSetMasterType(uid,yysubchannel_id,dc2ds_set_master_type_request)
    
    def Ondc2ds_change_role_request(self, uid, yychannel_id, yysubchannel_id, dc2ds_change_role_request):
        self._debug_logger.info("Ondc2ds_change_role_request uid = %d, yychannel_id = %d, yysubchannel_id = %d" % ( uid, yychannel_id, yysubchannel_id ))
        GetDrawChannelMgr().OnChangeRole(uid,yysubchannel_id,dc2ds_change_role_request)

    def Ondc2ds_chat_request(self, uid, yychannel_id, yysubchannel_id, dc2ds_chat_request):
        self._debug_logger.info("Ondc2ds_chat_request uid = %d, yychannel_id = %d, yysubchannel_id = %d" % ( uid, yychannel_id, yysubchannel_id ))
        GetDrawChannelMgr().OnChat(uid,yysubchannel_id,dc2ds_chat_request)
        
    def Ondc2ds_config_request(self, uid, yychannel_id, yysubchannel_id, dc2ds_config_request):
        self._debug_logger.info("Ondc2ds_config_request uid = %d, yychannel_id = %d, yysubchannel_id = %d" % ( uid, yychannel_id, yysubchannel_id ))
        GetDrawChannelMgr().OnConfig(uid,yysubchannel_id,dc2ds_config_request)
        
    def Ondc2ds_chat_config_request(self, uid, yychannel_id, yysubchannel_id, dc2ds_chat_config_request_obj):
        self._debug_logger.info("Ondc2ds_chat_config_request uid = %d, yychannel_id = %d, yysubchannel_id = %d" % ( uid, yychannel_id, yysubchannel_id ))
        GetDrawChannelMgr().OnChatConfig(uid,yysubchannel_id,dc2ds_chat_config_request_obj)
        
    def Ondc2ds_ping(self, uid, yychannel_id, yysubchannel_id, dc2ds_ping_obj):
        GetDrawUserMgr().OnPing(uid)
        
    def Ondc2ds_apply_drawer_request(self, uid, yychannel_id, yysubchannel_id, dc2ds_apply_drawer_request_obj):
        GetDrawChannelMgr().UserApply(uid,yysubchannel_id)
        
    def Ondc2ds_manage_channel_words_request(self, uid, yychannel_id, yysubchannel_id, dc2ds_manage_channel_words_request_obj):
        GetChannelDictionaryMgr().OnManageChannelWords( uid, yychannel_id, yysubchannel_id, dc2ds_manage_channel_words_request_obj )
        
    def Ondc2ds_update_channel_words_request(self, uid, yychannel_id, yysubchannel_id, dc2ds_update_channel_words_request_obj):
        GetChannelDictionaryMgr().OnUpdateChannelWords( uid, yychannel_id, yysubchannel_id, dc2ds_update_channel_words_request_obj )
        
    def Ondc2ds_submit_words_request(self, uid, yychannel_id, yysubchannel_id, dc2ds_submit_words_request_obj):
        GetChannelDictionaryMgr().OnSubmitWords( uid, yychannel_id, yysubchannel_id, dc2ds_submit_words_request_obj )
        
    def Ondc2ds_make_suggestions(self, uid, yychannel_id, yysubchannel_id, dc2ds_make_suggestions_obj):
        self._suggestion_logger.info("uid = %d, yychannel_id = %d, yysubchannel_id = %d, suggestion = %s" % ( uid, yychannel_id, yysubchannel_id, dc2ds_make_suggestions_obj.suggestions ))
        
    def Ondc2ds_login_launcher_request(self, uid, yychannel_id, yysubchannel_id, dc2ds_login_launcher_request_obj):
        if self.CheckClient(dc2ds_login_launcher_request_obj):
            #玩家点返回的处理
            res = dc2ds_logout_request()
            self.Ondc2ds_logout_request( uid, yychannel_id, yysubchannel_id, res )
        
            from datetime import date
            weeknum = date.today().isocalendar()[1]
            self._login_logger.info("week[%d] dc2ds_login_launcher_request uid = %d, yychannel_id = %d, yysubchannel_id = %d" % ( weeknum, uid, yychannel_id, yysubchannel_id ))
            GetDrawChannelMgr().OnUserEnterLauncher(uid, yychannel_id, yysubchannel_id)
        else:
            res = dc2ds_login_launcher_response()
            res.response = res.FAIL_INVALID_CLIENT_VERSION
            res.room_amount = 0
            res.name = ""
            res.channel_name = ""
            res.topchannel_id = yychannel_id
            self.SendMessage(uid,yychannel_id,res)
        
    def Ondc2ds_use_item_request(self, uid, yychannel_id, yysubchannel_id, dc2ds_use_item_request_obj):
        GetDrawChannelMgr().UseItemRequest( uid, yychannel_id, yysubchannel_id, dc2ds_use_item_request_obj)

    def Ondc2ds_get_score_request(self, uid, yychannel_id, yysubchannel_id, dc2ds_get_score_request_obj):
        GetDrawUserMgr().GetScoreRequest(uid,yychannel_id,yysubchannel_id,dc2ds_get_score_request_obj)
           
    def Ondc2ds_start_action_request(self, uid, yychannel_id, yysubchannel_id, dc2ds_start_action_request_obj):
        yychannel = GetDrawChannelMgr().GetDrawChannelByChannelId( yysubchannel_id )
        if yychannel is not None:
            yychannel.StartActionRequest(uid,dc2ds_start_action_request_obj)
    
    def Ondc2ds_stop_action_request(self, uid, yychannel_id, yysubchannel_id, dc2ds_stop_action_request_obj):
        yychannel = GetDrawChannelMgr().GetDrawChannelByChannelId( yysubchannel_id )
        if yychannel is not None:
            yychannel.StopActionRequest(uid,dc2ds_stop_action_request_obj)
           
g_draw_main = None
def GetDrawMainMgr():
    global g_draw_main
    if g_draw_main is None:
        g_draw_main = DrawMain()
    return g_draw_main

        