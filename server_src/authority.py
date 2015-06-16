# -*- coding:utf-8 -*-
'''
    file: authority.py
    auth: xuzhijian
    date: 2011-07-10
    desc: ���续��Ȩ�޿�������

    ���ݻ�������Ƽ����޹�˾ ��Ȩ���� (c) 2005-2011 DuoWan.com [������Ϸ]
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
        "_YYCHANNEL_NORMAL_ROLE" : 25,        #����
        "_YYCHANNEL_DELETED_ROLE" : 50,
        "_YYCHANNEL_TMPVIP_ROLE" : 66,        #������
        "_YYCHANNEL_VIP_ROLE" : 88,           #����
        "_YYCHANNEL_MEMBER_ROLE" : 100,       #����
        "_YYCHANNEL_CMANAGER_ROLE" : 150,     #���� ����
        "_YYCHANNEL_PMANAGER_ROLE" : 175,
        "_YYCHANNEL_MANAGER_ROLE" : 200,      #����
        "_YYCHANNEL_VICE_OWNER_ROLE" : 230,   #����
        "_YYCHANNEL_OWNER_ROLE" : 255,        #���� ow
        "_YYCHANNEL_KEFU_ROLE" : 300,
        "_YYCHANNEL_SA_ROLE" : 1000,          #����
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