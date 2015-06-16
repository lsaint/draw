# -*- coding:utf-8 -*-
'''
    file: net.py
    author: lSaint
    date: 2011-06-16
    desc: 你画我猜 网络框架

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

from dsf_protobuf_handle import *

from ctypes import *


def OnRecv(addr, length):
    cs = string_at(addr, length)
    GetConnectionCtrl().OnRecv(cs, length)


def OnConnect(ret):
    print "OnConnect"
    GetConnectionCtrl().OnConnect(ret)


def OnUserInfo(imid, name, ret):
    GetConnectionCtrl().OnUserInfo(imid, name, ret)


def OnClose():
    GetConnectionCtrl().OnClose()


pt_connect = CFUNCTYPE(None, c_int)
pt_recv = CFUNCTYPE(None, c_uint, c_uint)
pt_userinfo = CFUNCTYPE(None, c_uint, c_char_p, c_int)
pt_onclose = CFUNCTYPE(None)

fun_connect = pt_connect(OnConnect)
fun_recv = pt_recv(OnRecv)
fun_userinfo = pt_userinfo(OnUserInfo)
fun_onclose = pt_onclose(OnClose)



class ConnectionCtrl(object):

    def __init__(self):
        self.buf = ""
        self.callback= {}
        self.factory = None 

        self.sdk = cdll.LoadLibrary("ada.dll")
        self.sdk.Init.restype = c_int
        self.sdk.Connect.restype = c_int
        self.sdk.GetUserInfo.restype = c_int
        self.sdk.Init(fun_connect, fun_userinfo, fun_recv, fun_onclose)


    def SetProtobufIndex(self, dt, sid):
        '''必须在Connect之前设置 并用AddHandler注册相应回调'''
        self.factory = ProtobufMessageFactory(dt, sid)


    def AddHandler(self, pb_class, handler):
        self.callback[self.factory.GetPbUri(pb_class)] = (handler, pb_class)


    def Connect(self):
        self.sdk.Connect()

    
    def Send(self, data):
        self.sdk.Send(data, len(data))


    def SendPb(self, pb_ins):
        self.Send(self.factory.PackMessage(pb_ins))


    def OnRecv(self, data, length):
        self.buf = "%s%s" % (self.buf, data)
        while True:
            msg, self.buf = self.factory.ParseMessage(self.buf)
            if msg is None:
                break
            self.Dispatch(msg)


    def Dispatch(self, msg):
        uri = msg.GetUri()
        if uri <= 0:
            print "dispatch invalid uri"
            return 
        if uri in self.callback.keys():
            handler, pb_class = self.callback[uri]
            ins = pb_class()
            ins.ParseFromString(msg.GetBody())
            handler(ins)
        else:
            print "uri", uri
            print self.callback
            self.OnUnknownMessage(msg)
            

    def OnUnknownMessage(self, msg):
        print "UnknownMessage message"
 

    def OnConnect(self, ret):
        pass


    def OnUserInfo(self, imid, name, ret):
        self.userinfo_callback(imid, name, ret)


    def GetUserInfo(self, callback):
        self.sdk.GetUserInfo()
        self.userinfo_callback = callback


    def RegisterCloseCallback(self, func):
        self.close_callback = func


    def OnClose(self):
        if hasattr(self, "close_callback"):
            self.close_callback()


### 

g_conn = None
def GetConnectionCtrl():
    global g_conn
    if g_conn is None:
        g_conn = ConnectionCtrl()
    return g_conn

