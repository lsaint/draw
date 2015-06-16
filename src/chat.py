# -*- coding:utf-8 -*-
'''
    file: chat.py
    author: lSaint
    date: 2011-07-22
    desc: 聊天模块

    广州华多网络科技有限公司 版权所有 (c) 2005-2010 DuoWan.com [多玩游戏]
'''

from common import *
import draw_pb2
from draw_pb2 import *
from PyQt4 import QtCore
from qt_class import PopMenu
import time, random


class ChatMgr(object):

    def  __init__(self, game_mgr, window):
        self.window = window
        self.connection = game_mgr.connection
        self.uid_name = game_mgr.uid_name
        self.game = game_mgr
        self.chat_interval = 1
        self.last_chat_time = 0
        self.talk_mode =  None
        self.talk_target = draw_pb2.CHAT_TO_ALL 
        self.to_uid = 0

        self.CreateConnection()
        self.right_click_uid = None
        self.menu = PopMenu(self.window)
        self.menu.ConnectTalkToAction(self.OnClickedTalkTo)
        self.menu.ConnectSetHostAction(self.OnClickedSetHost)


    def CreateConnection(self):
        self.window.msg_view.name_clicked.connect(self.OnTextClick)
        self.window.box_talk_target.currentIndexChanged.connect(self.OnTalkTargetChange)

        self.shortcut_Return = QtGui.QShortcut(QtCore.Qt.Key_Return, self.window, self.PressEnter) 
        self.shortcut_Enter = QtGui.QShortcut(QtCore.Qt.Key_Enter, self.window, self.PressEnter) 


    def RegisterChatCallback(self):
        self.connection.AddHandler(ds2dc_chat_response, self.OnChatResponse)
        self.connection.AddHandler(ds2dc_chat_notification, self.OnChatNotification)
        self.connection.AddHandler(ds2dc_chat_config_response, self.OnChatConfigResponse)
        self.connection.AddHandler(ds2dc_chat_config_notification, self.OnChatConfigNotification)


    def CheckMatchKeyword(self,word):
        if word == self.game.standard_mgr.keyword:
            return True
        return False
        
        
    def CheckTalkInterval(self):
        return (True, False)[(time.time() - self.last_chat_time) < self.chat_interval]


    def SetAuthority(self, b):
        self.menu.is_admin = b


    def OnClickedSetHost(self):
        self.game.OnPopMenuTriggerd(self.right_click_uid, POP_MENU_SET_HOST)

    
    def OnClickedTalkTo(self):
        self.game.OnPopMenuTriggerd(self.right_click_uid, POP_MENU_TALK_TO)


    def Talk(self, msg):
        pure_msg = msg
        if msg == "" or pure_msg.replace(' ', '') == "":
            return
        if not self.CheckMatchKeyword(pure_msg) and not self.game.IsAdmin() and self.CheckTalkInterval() is False:
            self.ShowAnnounce(u"对不起，管理员限制打字间隔为%d秒，请稍后重试。" % self.chat_interval)
            return
        msg = self.CheckSpecialAction(msg)
        self.SendChat(msg, self.talk_target, self.to_uid)
        self.last_chat_time = time.time()
        self.window.chat_edit.SaveHistory()


    def CheckSpecialAction(self, msg):
        if msg.startswith(SP_ACTION_ROLL):
           return u"%s%d" % (SP_ACTION_ROLL, random.randint(0,100))     
        return msg


    def ParseSpecialAction(self, msg):
        if msg.startswith(SP_ACTION_ROLL):
            return msg[len(SP_ACTION_ROLL):]
        return msg


    def SendChat(self, msg, mode=draw_pb2.CHAT_TO_ALL, uid=0):
        pb = dc2ds_chat_request()
        pb.chat_mode = mode
        pb.chat_msg = msg
        if mode == draw_pb2.PRIVATE_CHAT:
            pb.target_uid = uid
        self.connection.SendPb(pb)


    def ConfigChat(self, mode, tuid=0, interval=0):
        pb = dc2ds_config_request()
        pb.config_mode = mode
        pb.target_uid = tuid
        pb.chat_interval = interval
        self.connection.SendPb(pb)


    def OnChatResponse(self, pb):
        print "OnChatResponse", pb.response_type
        if pb.response_type == pb.FAIL_NOT_PERMIT_TO_CHAT:
            self.ShowAnnounce(u"你没有发言权限")


    def OnChatNotification(self, pb):
        print "OnChatNotification", pb.chat_mode, pb.from_uid, self.game.uid
        suf = ""
        pre = ""
        color = ""
        name = self.GetShowName(pb.from_uid)
        name = self.FilterHtml(name)

        # 动作
        parse_ret = self.ParseSpecialAction(pb.chat_msg)
        if parse_ret != pb.chat_msg:
            return self.ShowAnnounce(u"%s掷出了%s点" % (name, parse_ret))

        # 系统
        if pb.chat_mode == draw_pb2.SYSTEM_CHAT:
            return self.ShowSystemTip(pb.chat_msg)

        save_uid = pb.from_uid
        # 旁观
        if pb.chat_mode == draw_pb2.CHAT_TO_WATCHER:
            suf = CHAT_STYLE_OBSERVER
            color = CHAT_COLOR_OBSERVER

        # 绘画
        elif pb.chat_mode == draw_pb2.CHAT_TO_PLAYER:
            suf = CHAT_STYLE_PLAYER
            color = CHAT_COLOR_PLAYER

        # 私聊
        elif pb.chat_mode == draw_pb2.PRIVATE_CHAT: 
            color = CHAT_COLOR_PRIVATE
            if pb.from_uid == self.game.uid:
                pre = CHAT_STYLE_PRIVATE_PRE
                name = self.GetShowName(pb.target_uid)
                save_uid = pb.target_uid
            else:
                suf = CHAT_STYLE_PRIVATE_SUF
        msg = u"%s<a href='%d'>%s</a>%s%s:%s"\
                % (pre, save_uid, name, suf, color, self.FilterHtml(pb.chat_msg))
        self.window.msg_view.append(msg)


    def FilterHtml(self, msg):
        return msg.replace(u"<", u"＜")#.replace(u">", u"＞")


    def GetShowName(self, uid):
        name = self.uid_name.get(uid, u"L'")
        if len(name) > MAX_CHAT_NAME_LEN:
            return name[:MAX_CHAT_NAME_LEN]
        return name


    def OnTextClick(self, data, button):
        if self.uid_name.get(int(data)) is None:
            return

        if button == QtCore.Qt.LeftButton:
            self.SetTalkTo(int(data))

        if button == QtCore.Qt.RightButton:
            self.right_click_uid = int(data)
            self.menu.Pop()


    def SetTalkTo(self, uid):
        print "SetTalkTo", uid
        if uid == self.game.uid:
            return
        self.to_uid = uid
        self.talk_target = draw_pb2.PRIVATE_CHAT
        
        idx = self.window.box_talk_target.findData(uid)
        if idx == -1:
            self.SaveTalkTarget(uid)
            idx = self.window.box_talk_target.count() - 1

        self.window.box_talk_target.setCurrentIndex(idx)
        self.window.chat_edit.setFocus()


    def OnTalkTargetChange(self, idx):
        '''0-all, 1-observer 2-player 3-Separator >4 recent talk target'''
        print "talk idx", idx, self.window.box_talk_target.itemData(idx)
        if idx == 0:
            self.talk_target = draw_pb2.CHAT_TO_ALL
        elif idx == 1:
            self.talk_target = draw_pb2.CHAT_TO_WATCHER
        elif idx == 2:
            self.talk_target = draw_pb2.CHAT_TO_PLAYER
        else: 
            to_uid = self.window.box_talk_target.itemData(idx)
            if to_uid is None:
                return
            self.talk_target = draw_pb2.PRIVATE_CHAT
            self.to_uid = to_uid
        self.window.chat_edit.setFocus()


    def SaveTalkTarget(self, uid):
        if self.window.box_talk_target.findData(uid) != -1:
            return
        if self.window.box_talk_target.count() >= MAX_CHAT_TARGET_COUNT:
            self.window.box_talk_target.removeItem(RECENT_TALK_BEGIN_INDEX) 
        self.window.box_talk_target.insertItem(MAX_CHAT_TARGET_COUNT, self.GetShowName(uid), uid)


    def ClearTalkTarget(self):
        cur = self.window.box_talk_target.count()
        if cur < RECENT_TALK_BEGIN_INDEX:
            return
        for i in range(RECENT_TALK_BEGIN_INDEX, cur):
            self.window.box_talk_target.removeItem(i)
        self.window.box_talk_target.setCurrentIndex(0)


    def ShowAnnounce(self, msg):
        self.window.msg_view.append(CHAT_COLOR_ANNOUNCE % msg)


    def SetTalkMode(self, mode):
        self.talk_mode = mode
        self.window.label_talk_mode.setText(NAME_TALK_MODE[mode])


    def RequestConfigTalkMode(self, mode):
        if self.talk_mode == mode:
            return
        print "RequestConfigTalkMode", mode
        pb = dc2ds_chat_config_request()
        pb.config_mode = mode
        self.connection.SendPb(pb)


    def OnConfigResponse(self, pb):
        print "interval", pb.chat_interval
        self.SetChatInterval(pb.chat_interval)
        self.ShowAnnounce(u"当前发言间隔被你设置为%s秒" % (pb.chat_interval))


    def OnConfigNotification(self, pb):
        self.SetChatInterval(pb.chat_interval)
        name = self.uid_name.get(pb.op_uid)
        self.ShowAnnounce(u"当前发言间隔被%s设置为%s秒" % (name, pb.chat_interval))
 

    def OnChatConfigResponse(self, pb):
        print "OnChatConfigResponse", pb.config_response
        self.SetTalkMode(pb.config_mode)
        self.ShowAnnounce(u"当前发言模式被你设置为 %s" % NAME_TALK_MODE[pb.config_mode])


    def OnChatConfigNotification(self, pb):
        print "OnChatConfigNotification", pb.op_uid, pb.config_mode
        name = self.uid_name.get(pb.op_uid)
        mode_name = NAME_TALK_MODE[pb.config_mode]
        self.SetTalkMode(pb.config_mode)
        self.ShowAnnounce(u"当前发言模式被%s设置为 %s" % (name, mode_name))


    def RequestSetChatInterval(self, sec):
        if sec == self.chat_interval:
            return
        print "RequestSetChatInterval sec", sec
        pb = dc2ds_config_request()
        pb.config_mode = CONFIG_SET_CHAT_INTERVAL
        pb.chat_interval = sec
        self.connection.SendPb(pb)


    def SetChatInterval(self, sec):
        print "SetChatInterval", sec
        self.chat_interval = sec
        #self.window.interval_box.setValue(sec)


    def PressEnter(self):
        if self.window.chat_edit.hasFocus():
            msg = self.window.chat_edit.text()
            print "chat msg", msg
            self.Talk(msg)
            self.window.chat_edit.clear()
        else:
            self.window.chat_edit.setFocus()


    def ShowSystemTip(self, tip):
        self.window.msg_view.append(CHAT_COLOR_SYSTEM % tip)

