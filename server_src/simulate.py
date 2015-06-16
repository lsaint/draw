# -*- coding:utf-8 -*-
'''
    file: simulate.py
    author: xuzhijian
    date: 2011-06-28
    desc: 机器人批量模拟客户端

    广州华多网络科技有限公司 版权所有 (c) 2005-2010 DuoWan.com [多玩游戏]
'''
#from PyQt4 import QtCore

import draw_logging
import logging

import api_yysession
from draw_main import *
from draw_channel_mgr import *
from pickle_event import *

import random

from draw_pb2 import *
from draw_common import *

AI_MODE_CHAT_ONLY = 1
AI_MODE_APPLY_DRAW = 2
AI_MODE_APPLY_DRAW_CHAT = 3
AI_MODE_LOGIN_ONLY = 4
AI_MODE_SILENT = 5
AI_MODE_MAX_AI = 5
AI_MODE_MIN_AI = 1

CHAT_WORDS = ["hold住了全场", "我饿了...", "好好玩啊，再战100盘！", "我困了", "你们太逊了", "无敌是最寂寞", "你画的是啥啊", "怎么总是有人进进出出", "哥不是机器人好吧", "未来是机器人的天下！", "谁说我是机器人我和谁急", "不想玩就退出，姐不拦你", ]

class Robot(object):
    def __init__(self, uid, ai_mode, ):
        self._scribble = ScribblePickle()
        self._ai_mode = ai_mode
        self._next_action_time = 0
        self._channel_id = 0
        self._topchannel_id = 0
        self._uid = uid
        self._name = ""
        self.GenName()
        
    def SetAI(self, ai_mode):
        self._ai_mode = ai_mode
        
    def GenName(self):
        self._name = "机器人%d号" % self._uid
    
    def GetName(self):
        return self._name
        
    def DoLogin(self, channel_id):
        if self.LocateChannel() != 0:
            return False
            
        chl_role_dict = {channel_id:150}
        api_yysession.OnPYYSessionOnNewUsers(self._uid, channel_id, self._name, chl_role_dict)
        
        channel = GetDrawChannelMgr().GetDrawChannelByChannelId(channel_id)
        if channel is None:
            return False
            
        self._channel_id = channel_id
        self._topchannel_id = channel._topchannel_id
        login_request = dc2ds_login_request()
        login_request.main_version = DrawConfig.CLIENT_MAIN_VERSION
        login_request.minor_version = DrawConfig.CLIENT_MINOR_VERSION
        GetDrawMainMgr().Ondc2ds_login_request(self._uid, self._topchannel_id, channel_id, login_request)
        print "DoLogin robot_uid=%d channel_id=%d name=%s" % ( self._uid, channel_id, self.GetName() )
        return True
        
    def DoLogout(self):
        if self.LocateChannel() == 0:
            return
            
        logout_request = dc2ds_logout_request()
        GetDrawMainMgr().Ondc2ds_logout_request( self._uid, self._topchannel_id, self.LocateChannel(), logout_request)
    
    def DoAction(self):
        if self.LocateChannel() == 0:
            return
            
        if self._ai_mode == AI_MODE_CHAT_ONLY:
            self.DoChat()
        elif self._ai_mode == AI_MODE_APPLY_DRAW:
            self.DoApply()
        elif self._ai_mode == AI_MODE_APPLY_DRAW_CHAT:
            self.DoApply()
            self.DoChat()
        elif self._ai_mode == AI_MODE_LOGIN_ONLY:
            self.DoApply()
            self.DoLogout()
            
        self.DoPing()
        
    def DoChat(self):
        if self.LocateChannel() == 0:
            return
    
        request = dc2ds_chat_request()
        if random.randint(1,10) <= 5:
            request.chat_mode = CHAT_TO_ALL
        else:
            request.chat_mode = CHAT_TO_WATCHER
            
        word_index = random.randint(0, len(CHAT_WORDS) - 1 )
        request.chat_msg = CHAT_WORDS[word_index].decode('utf-8')
        
        GetDrawMainMgr().Ondc2ds_chat_request(self._uid, self._topchannel_id, self.LocateChannel(), request)
    
    def DoApply(self):
        if self.LocateChannel() == 0:
            return
    
        request = dc2ds_apply_drawer_request()
        GetDrawMainMgr().Ondc2ds_apply_drawer_request(self._uid, self._topchannel_id, self.LocateChannel(), request)
        
    def RandomPoint(self):
        x = random.randint(1,700)
        y = random.randint(1,420)
        return (x,y)
        
    def SimulateDrawAction(self):
        flag = random.randint(1, 10)
        width_list = [3,9,18]
        for amount in range(1,random.randint(5,10)):
            if flag == 1:
                self._scribble.PickleScribbleEvent(WidthEvent(width_list[random.randint(0,len(width_list)-1)]))
            elif flag == 2:
                self._scribble.PickleScribbleEvent(RectEvent(self.RandomPoint(), self.RandomPoint()))
            elif flag == 3:
                self._scribble.PickleScribbleEvent(ElliEvent(self.RandomPoint(), self.RandomPoint()))
            else:
                self._scribble.PickleScribbleEvent(MPressEvent(self.RandomPoint()))
                for delta in range(0,random.randint(10,20)):
                    self._scribble.PickleScribbleEvent(PointEvent(self.RandomPoint()))
                self._scribble.PickleScribbleEvent(MReleaseEvent(self.RandomPoint()))
        
    def DoDraw(self):
        channel = GetDrawChannelMgr().GetDrawChannelByChannelId(self._channel_id)
        if channel is not None:
            self.SimulateDrawAction()
            new_draw = ds2dc_draw_action()
            new_draw.draw_action = self._scribble.Dumps()
            channel.SendMsgToDrawChannelUsrs( self._uid, new_draw )
        
    def DoPing(self):
        request = dc2ds_ping()
        GetDrawMainMgr().Ondc2ds_ping(self._uid, self._topchannel_id, self.LocateChannel(), request)
    
    def LocateChannel(self):
        return self._channel_id
        
    def OnTimer(self, time):
        channel = GetDrawChannelMgr().GetDrawChannelByChannelId(self._channel_id)
        if self._ai_mode == AI_MODE_SILENT:
            self.DoLogout()
        elif channel is not None and channel.GetMasterDrawId() == self._uid:
            self.DoDraw()
        elif time >= self._next_action_time:
            self._next_action_time = time + 10000 + random.randint(0,50000)
            self.DoAction()

    
class RobotMgr(object):
    def __init__(self):
        self._robots = {}
        self._channels = []
        self._last_uid = 50000000
        self._init = False
        self._init_time = 0
        self._run = False
        self._logger = logging.getLogger(draw_logging.LOGIC_DEBUG_LOG)
        
    def Init(self):
        return
        self.AddOperationChannel(10042778)
        self.AddOperationChannel(24481550)
    
        self.AddRobots( AI_MODE_CHAT_ONLY, 10 )
        self.AddRobots( AI_MODE_APPLY_DRAW, 10 )
        self.AddRobots( AI_MODE_APPLY_DRAW_CHAT, 10 )
        self.AddRobots( AI_MODE_LOGIN_ONLY, 20 )
            
        self._init = True
        print "RobotMgr Init finish !!"
  
    def ResetAI(self):
        for each_robot in self._robots.values():
            random_ai = random.randint(AI_MODE_MIN_AI,AI_MODE_MAX_AI-1)
            each_robot.SetAI(random_ai)
            
    def StartSimulate(self):
        if self._run:
            self._logger.info("StartSimulate fail ! it's running already")
            return False
        
        if not self._init:
            self.Init()
        else:
            self.ResetAI()
        
        for each_robot in self._robots.values():
            each_robot.DoLogin(self.GetAOperationChannel())
            
        self._run = True
        self._logger.info("StartSimulate ok")
        print "StartSimulate ok"
        return True
    
    def StopSimulate(self):
        if not self._run:
            self._logger.info("StopSimulate fail ! stoped already")
            return False
            
        for each_robot in self._robots.values():
            each_robot.SetAI(AI_MODE_SILENT)
            
        self._run = False
        self._logger.info("StopSimulate ok")
        return True
        
    def GetAOperationChannel(self):
        if len(self._channels) <= 0:
            return 0
        channel_index = random.randint(0,len(self._channels)-1)
        return self._channels[channel_index]
        
    def AddOperationChannel(self,channel_id):
        self._channels.append(channel_id)
    
    def AddRobots(self, ai_mode, amount):
        self._logger.info("AddRobots ai_mode=%d amount=%d" % (ai_mode, amount) )
        i = 0
        while i < amount:
            new_robot = Robot( self.GetNextRobotUid(), ai_mode )
            self._robots[new_robot._uid] = new_robot
            i = i + 1
    
    def OnTimer(self, timer_time):
        if not self._init:
            return
            
        if self._init_time == 0:
            self._init_time = timer_time
                        
        if not self._run:
            if self._init_time + 60000 <= timer_time:
                self.StartSimulate()
            return
            
        for each_robot in self._robots.values():
            each_robot.OnTimer(timer_time)
    
    def GetNextRobotUid(self):
        self._last_uid = self._last_uid + 1
        return self._last_uid
    
g_robot_mgr = None
def GetRobotMgr():
    global g_robot_mgr
    if g_robot_mgr is None:
        g_robot_mgr = RobotMgr()
    return g_robot_mgr