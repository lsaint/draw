# -*- coding:utf-8 -*-
'''
    file: chl_usr.py
    date: 2011-06-27
    desc: 用户UID到频道ID映射管理

    广州华多网络科技有限公司 版权所有 (c) 2005-2010 DuoWan.com [多玩游戏]
'''

#一个用户在一个顶级频道下整个频道树的权限
class UsrChlRole(object):
    def __init__(self, uid, yychannel_id, chl_role_dict ):
        self._uid = uid
        self._top_yychannel_id = yychannel_id
        self._chl_role_dict = chl_role_dict
        self.SetTopChannelDefaultRoleValue()
        
    def SetTopChannelDefaultRoleValue(self):
        if not self._chl_role_dict.has_key(self._top_yychannel_id):
            from authority import *
            self._chl_role_dict[self._top_yychannel_id] = GetAuthorityMgr().GetYYChannelValueFromRole("_YYCHANNEL_NORMAL_ROLE")
    
    def Update(self, yychannel_id, chl_role_dict ):
        self._top_yychannel_id = yychannel_id
        self._chl_role_dict = chl_role_dict
        self.SetTopChannelDefaultRoleValue()
        
    def RoleUpdate(self, yychannel_id, yysubchannel_id, type, role):
        if self._top_yychannel_id == yychannel_id:
            if type == 0 or type == 2:  # 0新角色，1删除角色，2变更角色
                self._chl_role_dict[yysubchannel_id] = role
            elif type == 1:
                if self._chl_role_dict.has_key(yysubchannel_id):
                    del self._chl_role_dict[yysubchannel_id]
        
    def GetChlRole(self, yychannel_id):
        parent_channel_id = GetAllChlPChlMgr().GetParentChannel(yychannel_id)
        channel_role = self._chl_role_dict.get(yychannel_id)
        parent_channel_role = self._chl_role_dict.get(parent_channel_id)
        top_channel_role = self._chl_role_dict.get(self._top_yychannel_id)
        
        max_role = channel_role
        if max_role is None or max_role < parent_channel_role:
            max_role = parent_channel_role
        if max_role is None or max_role < top_channel_role:
            max_role = top_channel_role

        return max_role
            
    def AddChlRole(self, yychannel_id, role):
        self._chl_role_dict[yychannel_id] = role
    
class AllUsrChlRoleMgr(object):
    usr_chls_role = {} # { uid : UsrChlRole() }
    
    def OnUsrAddChlRole(self, uid, yychannel_id, chl_role_dict ):
        AllUsrChlRoleMgr.usr_chls_role.setdefault( uid, {yychannel_id:role} )
        AllUsrChlRoleMgr.usr_chls_role[uid][yychannel_id] = role
        
    def ClearUsrChlRole(self, uid):
        if AllUsrChlRoleMgr.usr_chls_role.has_key(uid):
            del AllUsrChlRoleMgr.usr_chls_role[uid]
        
    def OnUsrLeaveChl(self, uid):
        self.ClearUsrChlRole(uid)       
        
    def UpdateUsrChlRole(self, uid, yychannel_id, chl_role_dict):
        user = self.GetUsrRole(uid)
        if user is None:
            user = UsrChlRole(uid, yychannel_id, chl_role_dict)
            AllUsrChlRoleMgr.usr_chls_role[uid] = user
        else:
            user.Update(yychannel_id, chl_role_dict)

    def OnUserInfoUpdate(self, uid, yychannel_id, chl_role_dict):
        self.UpdateUsrChlRole(uid, yychannel_id, chl_role_dict)
            
    def OnUsrEnterChl(self, uid, yychannel_id, chl_role_dict):
        self.UpdateUsrChlRole(uid, yychannel_id, chl_role_dict)
            
    def OnUserRoleUpdate(self, uid, yychannel_id, yysubchannel_id, type, role):
        user = self.GetUsrRole(uid)
        if user is not None:
            user.RoleUpdate(yychannel_id, yysubchannel_id, type, role)
    
    def GetUsrRole(self, uid):
        return AllUsrChlRoleMgr.usr_chls_role.get(uid)
    
    def GetUsrChlRole(self, uid, yychannel_id):
        usr_channel_role = AllUsrChlRoleMgr.usr_chls_role.get(uid)
        if usr_channel_role is not None:
            return usr_channel_role.GetChlRole(yychannel_id)
        else:
            from authority import *
            return GetAuthorityMgr().GetYYChannelValueFromRole("_YYCHANNEL_NORMAL_ROLE")

class AllUsrChlMgr(object):

    usr2chl = {} # {uid:chl}
    chl2usr = {} # {chl:[uid1,uid2...] ...}
    
    def GetChlFromUsr(self, uid):
        return AllUsrChlMgr.usr2chl.get(uid, 0)

    def GetUsrsFromChl(self, chl):
        return AllUsrChlMgr.chl2usr.get(chl,None)
            
    def GetUsr2Chl(self):
        return AllUsrChlMgr.usr2chl


    def GetChl2Usr(self):
        return AllUsrChlMgr.chl2usr

    def OnUserSubChannelChange(self, uid, yychannel_id):
        last_channel_id = AllUsrChlMgr.usr2chl.get(uid,0)
        if last_channel_id != 0:
            self.OnUsrLeaveChl(uid, last_channel_id)
            self.OnUsrEnterChl(uid, yychannel_id)
            
        return last_channel_id
        
    def OnUsrEnterChl(self, uid, yychannel_id):
        AllUsrChlMgr.usr2chl[uid] = yychannel_id
        AllUsrChlMgr.chl2usr.setdefault(yychannel_id, []).append(uid)


    def OnUsrLeaveChl(self, uid, yychannel_id):
        if AllUsrChlMgr.usr2chl.has_key(uid):
            del AllUsrChlMgr.usr2chl[uid]
        
        #session在OnUsrLeaveChl只会传根频道号来，但是假如用户此时在子频道的话，需要清除的是子频道房间的用户数据
        last_channel = AllUsrChlMgr.usr2chl.get(uid,0)
        if last_channel == 0:
            last_channel = yychannel_id
        lt = AllUsrChlMgr.chl2usr.get(last_channel)
        if lt is None or len(lt) == 0:
            return
        if uid in lt:
            lt.remove(uid)

    def IsUsrInChl(self, uid, yychannel_id):
        return AllUsrChlMgr.usr2chl.get(uid) == yychannel_id

class AllChlPChlMgr():
    chl2pchl = {} # {chl:pchl}
    def UpdateParentChannel(self, yychannel_id,parent_yychannel_id):
        AllChlPChlMgr.chl2pchl[yychannel_id] = parent_yychannel_id
        
    def GetParentChannel(self, yychannel_id):
        return AllChlPChlMgr.chl2pchl.get(yychannel_id, yychannel_id)
        
        
g_all_usr_chl_role_mgr = None
def GetAllUsrChlRoleMgr():
    global g_all_usr_chl_role_mgr
    if g_all_usr_chl_role_mgr is None:
        g_all_usr_chl_role_mgr = AllUsrChlRoleMgr()
    return g_all_usr_chl_role_mgr

g_all_usr_chl_mgr = None
def GetAllUsrChlMgr():
    global g_all_usr_chl_mgr
    if g_all_usr_chl_mgr is None:
        g_all_usr_chl_mgr = AllUsrChlMgr()
    return g_all_usr_chl_mgr

g_all_chl_pchl_mgr = None
def GetAllChlPChlMgr():
    global g_all_chl_pchl_mgr
    if g_all_chl_pchl_mgr is None:
        g_all_chl_pchl_mgr = AllChlPChlMgr()
    return g_all_chl_pchl_mgr