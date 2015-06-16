# -*- coding:utf-8 -*-
'''
    file: api_yysession.py
    author: xuzhijian
    date: 2011-06-25
    desc: 用户频道，名字等信息的更新接口

    广州华多网络科技有限公司 版权所有 (c) 2005-2010 DuoWan.com [多玩游戏]
'''
import chl_usr
import uid_name

from draw_dictionary import *
from draw_dao import *
from draw_pb2 import *

def ConvertToPyDict(chl_role_dict):
    _chl_role_dict = {}
    for key in chl_role_dict.keys():
        _chl_role_dict[key] = chl_role_dict[key]
    return _chl_role_dict

def OnPGetAsidBySidRes(channel_id, short_channel_id, status):
    if status != 0:
        return False
        
    uid_name.GetShortChannelIdMgr().UpdateShortChannelId(int(channel_id), int(short_channel_id))
    return True
    
def OnPYYSessionOnYYChannelDestroy(yychannel_id):
	return True
	
def OnPYYSessionOnNewUsers(uid, yychannel_id, name, chl_role_dict):
    _chl_role_dict = ConvertToPyDict(chl_role_dict)
    uid_name.GetUidNameMgr().OnUserEnterChannel(uid, name)
    chl_usr.GetAllUsrChlMgr().OnUsrEnterChl(uid, yychannel_id)
    chl_usr.GetAllUsrChlRoleMgr().OnUsrEnterChl(uid, yychannel_id, _chl_role_dict)
    #print "OnPYYSessionOnNewUsers = %d, %d, %s" % (uid, yychannel_id, name)

def OnPYYSessionOnUserSubChannelChange(uid, yychannel_id, yysubchannel_id):
    last_channel_id = chl_usr.GetAllUsrChlMgr().OnUserSubChannelChange(uid, yysubchannel_id)
    from draw_channel_mgr import *
    GetDrawChannelMgr().OnUserSubChannelChange(uid,yychannel_id, yysubchannel_id, last_channel_id)
    #print "OnPYYSessionOnUserSubChannelChange = %d, %d, %d" % (uid, yychannel_id, yysubchannel_id)
    
def OnPYYSessionOnUserInfoUpdate(uid, yychannel_id, name, chl_role_dict):
    _chl_role_dict = ConvertToPyDict(chl_role_dict)
    uid_name.GetUidNameMgr().OnUserInfoUpdate(uid, name)
    chl_usr.GetAllUsrChlRoleMgr().OnUserInfoUpdate(uid, yychannel_id, _chl_role_dict)
    #print "OnPYYSessionOnUserInfoUpdate = %d, %d, %s" % (uid, yychannel_id, name)
    
def OnPYYSessionGetYYChannelInfoResponse(yychannel_id, parent_yychannel_id, name):
    uid_name.GetYYChannelidNameMgr().OnChannelInfoUpdate(yychannel_id, name)
    chl_usr.GetAllChlPChlMgr().UpdateParentChannel(yychannel_id,parent_yychannel_id)
    #print "OnPYYSessionGetYYChannelInfoResponse = %d, [%s]" % (yychannel_id, name)
    
def OnPYYSessionOnUserMsg(uid, yychannel_id, yysubchannel_id, user_msg):
    from draw_main import *
    #print "OnPYYSessionOnUserMsg = %d, %d, %d, %d" % (uid, yychannel_id, yysubchannel_id, len(user_msg) )
    GetDrawMainMgr().dataReceived(uid, yychannel_id, yysubchannel_id, user_msg)

def OnPYYSessionOnRemoveUsers(uid, yychannel_id):
    from draw_channel_mgr import *
    GetDrawChannelMgr().OnUserLeaveDraw(uid,yychannel_id)
    chl_usr.GetAllUsrChlMgr().OnUsrLeaveChl(uid, yychannel_id)
    
def OnPYYSessionOnUserRoleUpdate(uid, yychannel_id, yysubchannel_id, type, role):
    #print "OnPYYSessionOnUserRoleUpdate = %d, %d, %d, %d, %d" % (uid, yychannel_id, yysubchannel_id, type, role )
    chl_usr.GetAllUsrChlRoleMgr().OnUserRoleUpdate(uid, yychannel_id, yysubchannel_id, type, role)
    
def OnPYYSessionOnPreHalt():
    from draw_channel_mgr import *
    GetDrawChannelMgr().OnPreHalt()
    
    GetDrawDao().SaveDrawDictionary()

def OnInitSrv():
    import draw_logging
    import sys
    draw_logging.init_draw_logging()
    
    reload(sys)
    sys.setdefaultencoding('utf-8')
    
    #if not GetDrawDao().Open('127.0.0.1', 6208, 'app_db', 'root', '&2Hk9&Vbx@Aa'):
    if not GetDrawDao().Open('localhost', 3306, 'app_db', 'root', '218'):
        print 'OnInitSrv Open Dao Error !!'
        return False
    
    GetFullDicttionary().InitDict()
    GetChannelDictionaryMgr().InitDict()
        
    #模拟客户端压力测试
    #from simulate import *
    #GetRobotMgr().Init()
        
    return True
    
def OnTimer(timer_time):
    from draw_channel_mgr import *
    GetDrawChannelMgr().OnTimer(timer_time)
    
    from draw_user_mgr import *
    GetDrawUserMgr().OnTimer(timer_time)
    
    from simulate import *
    GetRobotMgr().OnTimer(timer_time)