# -*- coding:utf-8 -*-
'''
    file: api_service.py
    author: xuzhijian
    date: 2011-06-27
    desc: 画板用户发来的交互信息

    广州华多网络科技有限公司 版权所有 (c) 2005-2010 DuoWan.com [多玩游戏]
'''
from draw_main import *

def OnDrawClientMsg(cid, msg, size):
    print "OnDrawClientMsg = %d, %d, %d" % ( cid, len(msg), size)
    GetDrawMainMgr().dataReceived(0, cid, msg)
    
def OnClientDisconnect(cid):
    print "OnClientDisconnect = %d" % ( cid )
    
