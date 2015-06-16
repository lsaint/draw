# -*- coding:utf-8 -*-
'''
    file: uid_name.py
    date: 2011-06-27
    desc: 用户UID到昵称的映射表管理器

    广州华多网络科技有限公司 版权所有 (c) 2005-2010 DuoWan.com [多玩游戏]
'''


class UidNameMgr(object):
    
    uid_name = {} # {uid:name}

    def __init__(self):
        pass


    def OnUserEnterChannel(self, uid, name):
        self.OnUserInfoUpdate(uid, name)


    def OnUserLeaveChannel(self, uid):
        pass


    def OnUserInfoUpdate(self, uid, name):
        name = name.decode('utf-8')
        if self.uid_name.get(uid) != name:
            self.uid_name[uid] = name


    def GetUserName(self, uid):
        return self.uid_name.get(uid, "")

class YYChannelidNameMgr(object):
    
    channelid_name = {} # {uid:name}

    def OnChannelInfoUpdate(self, yysubchannel_id, name):
        name = name.decode('utf-8')
        if self.channelid_name.get(yysubchannel_id) != name:
            #print "OnChannelInfoUpdate %d = [%s]" % (yysubchannel_id, name)
            self.channelid_name[yysubchannel_id] = name

    def GetChannelName(self, yysubchannel_id):
        return self.channelid_name.get(yysubchannel_id, "")

class ShortChannelIdMgr(object):
    topchannel_shortchannel = {}
    def UpdateShortChannelId(self, topchannel_id, short_channel_id):
        if self.topchannel_shortchannel.get(topchannel_id, 0) != short_channel_id:
            print "UpdateShortChannelId topchannel_id=[%d] short_channel_id=[%d]" % (topchannel_id, short_channel_id)
            self.topchannel_shortchannel[topchannel_id] = short_channel_id
            
    def GetShortChannelId(self, topchannel_id):
        return self.topchannel_shortchannel.get(topchannel_id, topchannel_id)
   
    def NewTopChannel(self, topchannel_id):
        if not self.topchannel_shortchannel.has_key(topchannel_id):
            from draw_main import *
            print "NewTopChannel = %d" % topchannel_id
            GetDrawMainMgr().PyGetAsidBySid(topchannel_id)
        
   
g_short_channel_id_mgr = None
def GetShortChannelIdMgr():
    global g_short_channel_id_mgr
    if g_short_channel_id_mgr is None:
        g_short_channel_id_mgr = ShortChannelIdMgr()
    return g_short_channel_id_mgr

g_yy_channel_name_mgr = None
def GetYYChannelidNameMgr():
    global g_yy_channel_name_mgr
    if g_yy_channel_name_mgr is None:
        g_yy_channel_name_mgr = YYChannelidNameMgr()
    return g_yy_channel_name_mgr
        
g_unmgr = None
def GetUidNameMgr():
    global g_unmgr
    if g_unmgr is None:
        g_unmgr = UidNameMgr()
    return g_unmgr



