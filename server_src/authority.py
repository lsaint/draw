# -*- coding:utf-8 -*-
'''
    file: authority.py
    auth: xuzhijian
    date: 2011-07-10
    desc: 网络画板权限控制中心

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''



class AuthorityMgr(object):
    _yychannel_netborad_master_type_authority = {
        0   : False,
        20  : False,
        25  : False,
        50  : False,
        66  : False,
        88  : False,
        100 : False,
        150 : True,
        175 : True,
        200 : True,
        230 : True,
        255 : True,
        300 : True,
        1000: True,
    }
    
    _yychannel_role2value_dict = {
        "_YYCHANNEL_NUL_ROLE" : 0,
        "_YYCHANNEL_VISITOR_ROLE" : 20,
        "_YYCHANNEL_NORMAL_ROLE" : 25,        #白马
        "_YYCHANNEL_DELETED_ROLE" : 50,
        "_YYCHANNEL_TMPVIP_ROLE" : 66,        #亮绿马
        "_YYCHANNEL_VIP_ROLE" : 88,           #绿马
        "_YYCHANNEL_MEMBER_ROLE" : 100,       #蓝马
        "_YYCHANNEL_CMANAGER_ROLE" : 150,     #红马 粉马
        "_YYCHANNEL_PMANAGER_ROLE" : 175,
        "_YYCHANNEL_MANAGER_ROLE" : 200,      #黄马
        "_YYCHANNEL_VICE_OWNER_ROLE" : 230,   #橙马
        "_YYCHANNEL_OWNER_ROLE" : 255,        #紫马 ow
        "_YYCHANNEL_KEFU_ROLE" : 300,
        "_YYCHANNEL_SA_ROLE" : 1000,          #黑马
    }
    
    def GetYYChannelValueFromRole(self, role_str):
        return AuthorityMgr._yychannel_role2value_dict.get(role_str, 25)
    
    def GetMasterTypeAuthority(self, role):
        return AuthorityMgr._yychannel_netborad_master_type_authority.get(role, False)
        
    def GetConfigAuthority(self, role):
        return AuthorityMgr._yychannel_netborad_master_type_authority.get(role, False)
    
g_auth_mgr = None
def GetAuthorityMgr():
    global g_auth_mgr
    if g_auth_mgr is None:
        g_auth_mgr = AuthorityMgr()
    return g_auth_mgr