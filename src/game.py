# -*- coding:utf-8 -*-
'''
    file: game.py
    author: lSaint
    date: 2011-08-1
    desc: 游戏模块

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''


import sys, os
from net import GetConnectionCtrl
from common import *
import draw_pb2
from draw_pb2 import *
from chat import ChatMgr
from standard_mode import StandardModeMgr
from word import WordMgr
from PyQt4 import QtCore, QtGui

from game_state import GameMachine
from appraise_panel import AppraisePanel
from card_info import DetailedCard, MyCard, HostCard
from upload_worker import GetUploadMgr


class GameMgr(GameMachine):

    uid_name = {}

    def __init__(self, launcher, window):
        super(GameMgr, self).__init__(window)
        self.uid = None
        self.launcher = launcher
        self.log_file = sys.executable + ".log"
        self.connection = GetConnectionCtrl()
        self.connection.SetProtobufIndex(DRAW_PROTOCOL_ID_DICT, DRAW_SERVICE_ID)

        self.chat_mgr = ChatMgr(self, window)
        self.standard_mgr = StandardModeMgr(self, window, self.connection)
        self.word_mgr = WordMgr(self, window)
        self.appraise_panel = AppraisePanel(window, self)
        self.detail_card = DetailedCard(window, self)
        self.my_card = MyCard(self, window)
        self.host_card = HostCard(self, window)

        self.RegisterCallback()
        self.connection.Connect()
        self.connection.RegisterCloseCallback(self.OnDisConnect)
        self.LoginLauncher()
        self.remain_time = 0

        self.room_type = 0
        self.game_mode = ALTERNATION_TURN # 轮流
        self.game_role = WATCHER_ROLE # 观看
        self.yy_role = draw_pb2.APP_YYCHANNEL_NUL_ROLE
        self.yy_name = ""
        self.chl_name = ""
        self.chl_id = 0
        self.short_chl_id = 0
        self.cur_host_uid = 0

        self.upload_module = None
        self.CreateTimer()


    def InitUI(self):
        self.window.game = self
        self.window.CreateConnection()

        self.launcher.game = self
        self.launcher.CreateConnection()


    def LoginLauncher(self):
        pb = dc2ds_login_launcher_request()
        pb.main_version = MAIN_VERSION
        pb.minor_version = MINOR_VERSION
        self.connection.SendPb(pb)


    def WriteLog(self, msg):
        try:
            f = open(self.log_file, "w")
            f.write(msg)
            f.close()
        except:
            return


    def GetUsrName(self, uid):
        return self.uid_name.get(uid, "")
    

    def CreateTimer(self):
        self.SetTimer(SEND_INTERVAL, self.OnSendTimer)
        self.SetTimer(COUNT_INTERVAL, self.OnCounter)


    # 定时发送绘图数据
    def OnSendTimer(self):
        raw_data = self.window.scribbleArea.Dumps()
        if raw_data is None:
            return
        pb = dc2ds_master_draw_action()
        pb.draw_action = raw_data
        self.connection.SendPb(pb)


    def OnCounter(self):
        if self.remain_time == 0:
            return
        self.remain_time -= 1
        self.window.label_time.setText(unicode(self.remain_time))


    # 定时器封装
    def SetTimer(self, interval, callback, single=False):
        timer = QtCore.QTimer(self.window)
        if single:
            timer.setSingleShot(True)
        timer.start(interval)
        timer.timeout.connect(callback)
        return timer


    def Countdown(self, sec):
        self.remain_time = sec
        self.window.label_time.setText(unicode(self.remain_time))


    def StartPing(self):
        self.SetTimer(PING_INTERVAL, self.OnPingTimer)


    def OnPingTimer(self):
        from time import ctime
        print "ping", ctime()
        self.connection.SendPb(dc2ds_ping())


    def IsAdmin(self):
        if self.yy_role >= AUTHORITY_BONUD:
            return True
        return False


    def OnDisConnect(self):
        print "OnDisConnect"
        self.LogoutMain()
        self.ForceClose()


    def OnGetUserInfo(self, imid, name, ret):
        print "OnGetUserInfo", imid, name
        self.WriteLog("%s %s\n" % (imid, name))


    def SetGameMode(self, mode):
        print "SetGameMode", mode
        self.game_mode = mode
        self.window.label_game_mode.setText(NAME_GAME_MODE[mode])

        if mode == draw_pb2.ALTERNATION_TURN: 
            print "ALTERNATION_TURN"
            self.EnterAlternationState()

        if mode == draw_pb2.PRESIDING_TURN:
            print "PRESIDING_TURN"
            self.EnterPreSideState()

        if mode == draw_pb2.STANDRAD_TURN:
            print "STANDRAD_TURN"
            self.EnterStandardState()


    def RequestSetGameMode(self, mode):
        print "RequestSetGameMode"
        if mode == self.game_mode:
            return
        pb = dc2ds_set_master_type_request()
        pb.master_type = mode
        pb.drawer_id = self.uid
        pb.second = 0
        self.connection.SendPb(pb)


    def OnSetGameModeResponse(self, pb):
        print "OnSetGameModeResponse master_type %d, drawer_id %d second %d set_response %d"\
                % (pb.master_type, pb.drawer_id, pb.second, pb.set_response)
        if pb.set_response == pb.OK:
            self.SetGameMode(pb.master_type)
            self.chat_mgr.ShowAnnounce(u"你把应用模式设置为 %s"\
                    % NAME_GAME_MODE[pb.master_type])
            self.standard_mgr.OnGameModeChanged(pb.master_type)
            return

        if pb.set_response == pb.FAIL_ERROR_OP_AUTHORITY:
            self.chat_mgr.ShowAnnounce(TIP_NO_AUTHORITY)
            return

        if pb.set_response == pb.FAIL_BE_THE_MASTER_TYPE_ALREADY:
            self.chat_mgr.ShowAnnounce(TIP_RE_SETTING)
            return



    def RequestSetGameRole(self, uid, role):
        print "RequestSetGameRole", role
        pb = dc2ds_change_role_request()
        pb.target_uid = uid
        pb.role_type = role
        self.connection.SendPb(pb)
        

    def OnSetGameRoleResponse(self, pb):
        print "OnSetGameRoleResponse", pb.change_response
        if pb.change_response == pb.OK:
            self.SetGameRole(pb.target_uid, pb.role_type)
            if pb.target_uid == self.uid:
                return
            target_name = self.GetUsrName(pb.target_uid)
            self.chat_mgr.ShowAnnounce(u"你把%s设置为%s" % (target_name, NAME_ROLE[pb.role_type]))
            return

        if pb.change_response == pb.FAIL_ERROR_OP_AUTHORITY:
            self.chat_mgr.ShowAnnounce(TIP_NO_AUTHORITY)
            return 

        if pb.change_response == pb.FAIL_BE_THE_ROLE_ALREADY:
            self.chat_mgr.ShowAnnounce(TIP_RE_SETTING)
            return

        if pb.FAIL_ERROR_TURN == pb.FAIL_ERROR_TURN:
            if pb.target_uid == self.uid and self.game_mode == draw_pb2.PRESIDING_TURN:
                self.chat_mgr.ShowAnnounce(u"当前模式不允许改变身份")
            else:
                self.chat_mgr.ShowAnnounce(u"当前模式不允许设置主笔")
            return

        if pb.FAIL_PLAYER_FULL == pb.FAIL_PLAYER_FULL:
            self.chat_mgr.ShowAnnounce(u"画手列表已满")
            return


    def SetYYRole(self, role):
        self.yy_role = role
        if self.IsAdmin():
            self.window.button_setting.setDisabled(False)
            self.SetPopMenuAuthority(True)
        else:
            self.SetPopMenuAuthority(False)
            self.window.button_setting.setDisabled(True)


    def SetPopMenuAuthority(self, flag):
        print "SetPopMenuAuthority"
        if flag:
            self.window.player_list.SetAuthority(True)
            self.window.observer_list.SetAuthority(True)
            self.chat_mgr.SetAuthority(True)
        else:
            self.window.player_list.SetAuthority(False)
            self.window.observer_list.SetAuthority(False)
            self.chat_mgr.SetAuthority(False)


    def OnSetYYRole(self, pb):
        self.SetYYRole(pb.yyrole_type)
 

    def RegisterCallback(self):
        print "RegisterCallback"
        self.connection.AddHandler(ds2dc_draw_action, self.OnDrawAction)
        self.connection.AddHandler(ds2dc_login_response, self.OnLoginMainResponse)
        self.connection.AddHandler(ds2dc_add_drawer_list, self.OnAddPlayer)
        self.connection.AddHandler(ds2dc_remove_drawer_list, self.OnRemoveDrawerList)
        self.connection.AddHandler(ds2dc_set_master_drawer, self.OnSetHost)
        self.connection.AddHandler(ds2dc_set_master_type_response, self.OnSetGameModeResponse)
        self.connection.AddHandler(ds2dc_set_master_type_notification, self.OnSetGameModeNotification)
        self.connection.AddHandler(ds2dc_change_role_response, self.OnSetGameRoleResponse)
        self.connection.AddHandler(ds2dc_change_yyrole_notification, self.OnSetYYRole)
        self.connection.AddHandler(ds2dc_change_role_notification, self.OnSetGameRoleNotification)
        self.connection.AddHandler(ds2dc_change_subchannel, self.OnChangeSubchannel)
        self.connection.AddHandler(ds2dc_quit_notification, self.OnQuitNotification)

        self.connection.AddHandler(ds2dc_config_response, self.OnConfigResponse)
        self.connection.AddHandler(ds2dc_config_notification, self.OnConfigNotification)

        self.chat_mgr.RegisterChatCallback()
        self.standard_mgr.RegisterStandardModeCallback()
        self.word_mgr.RegisterSumitWordCallback()

        self.connection.AddHandler(dc2ds_login_launcher_response, self.launcher.OnLoginLauncherResponse)
        self.appraise_panel.RegisterItemPannelCallback()
        self.connection.AddHandler(ds2dc_get_score_response, self.OnGetScoreResponse)


    def OnConfigResponse(self, pb):
        print "OnConfigResponse config_type", pb.config_mode
        if pb.config_mode == CONFIG_SET_CHAT_INTERVAL:
            self.chat_mgr.OnConfigResponse(pb)
        elif pb.config_mode == CONFIG_SET_CHANNEL_DICTIONARY_RATE:
            self.word_mgr.OnSetChlWordRateResponse(pb)


    def OnConfigNotification(self, pb):
        print "OnConfigNotification, op_uid, config_mode", pb.op_uid, pb.config_mode
        if pb.config_mode == CONFIG_SET_CHAT_INTERVAL:
            self.chat_mgr.OnConfigNotification(pb)
        elif pb.config_mode == CONFIG_SET_CHANNEL_DICTIONARY_RATE:
            self.word_mgr.OnSetChlWordRateNotification(pb)


    # 服务器重启    
    def OnQuitNotification(self, pb):
        self.ForceClose()


    def OnChangeSubchannel(self, pb):
        print  "OnChangeSubchannel"
        self.window.player_list.Clear()
        self.window.observer_list.Clear()
        self.window.msg_view.clear()
        self.chat_mgr.ClearTalkTarget()
        self.window.scribbleArea.is_host = False
        self.window.scribbleArea.clearImage()
        self.InitGameInfo(pb)


    def InitGameInfo(self, pb):
        self.window.label_iminfo.setStyleSheet(u"color: %s;" % ROOM_COLOE.get(self.room_type, "black"))
        self.window.label_iminfo.setText(u"%s (%d)" % (pb.channel_name, pb.channel_id))
        self.window.label_imname.setText(u"%s" % pb.name)
        self.SetGameMode(pb.master_type)
        self.SetGameRole(self.uid, pb.role_type)
        self.SetYYRole(pb.yyrole_type)
        self.chat_mgr.SetChatInterval(pb.chat_interval)
        self.chat_mgr.SetTalkMode(pb.chat_config_mode)
        self.word_mgr.SetChlWordRate(pb.channel_dictionary_rate)


    def OnSetGameModeNotification(self, pb):
        print "OnSetGameModeNotification operation_uid %d master_type %d drawer_id %d second %d"\
                % (pb.operation_uid, pb.master_type, pb.drawer_id, pb.second)
        self.SetGameMode(pb.master_type)
        self.SetHost(pb.drawer_id)
        self.chat_mgr.ShowAnnounce(u"%s把应用模式设置为 %s"\
                % (self.GetUsrName(pb.operation_uid), NAME_GAME_MODE[pb.master_type]))
        self.standard_mgr.OnGameModeChanged(pb.master_type)


    def OnSetGameRoleNotification(self, pb):
        print "OnSetGameRoleNotification", pb.target_uid_list
        for target_uid in pb.target_uid_list:
            self.SetGameRole(target_uid, pb.role_type)
            if target_uid == pb.operation_uid or pb.operation_uid == 0:
                continue
            op_name = self.GetUsrName(pb.operation_uid)
            target_name = self.GetUsrName(target_uid)
            self.chat_mgr.ShowAnnounce(u"%s把%s设置为%s" % (op_name, target_name, NAME_ROLE[pb.role_type]))


    def ForceClose(self):
        print " ForceClose"
        self.window.scribbleArea.modified = False
        self.window.close()


    def LoginMain(self, room_type):
        pb = dc2ds_login_request()
        pb.main_version = MAIN_VERSION
        pb.minor_version = MINOR_VERSION
        pb.room_type = room_type 
        self.connection.SendPb(pb)
        self.room_type = room_type
        print "send loging request"


    def LogoutMain(self):
        print "logout"
        pb = dc2ds_logout_request()
        self.connection.SendPb(pb)


    def BackToLauncher(self):
        print "BackToLauncher"
        pb = dc2ds_logout_request()
        self.connection.SendPb(pb)
        self.LoginLauncher()
        self.window.ResetUI()
        self.Reset()
        self.EnterLoadingState()


    def Reset(self):
        self.cur_host_uid = 0
        self.standard_mgr.Reset()


    def SetUidName(self, uid, name):
        self.uid_name[uid] = name


    def OnAddPlayer(self, pb):
        print "OnAddPlayer", pb.amount
        for dm in pb.draw_member:
            self.SetUidName(dm.uid, dm.name)

            if not dm.watch:
                # player
                #self.window.player_list.OnPlayerEnter(dm.uid, dm.name)
                self.SetGameRole(dm.uid, PLAYER_ROLE)

                if dm.draw: # drawer
                    #self.window.player_list.SetHost(dm.uid)
                    self.SetHost(dm.uid, DRAWING_ROLE)

            else: # watcher
                #self.window.observer_list.OnPlayerEnter(dm.uid, dm.name)
                self.SetGameRole(dm.uid, WATCHER_ROLE)


    def OnDrawAction(self, pb):
        print "OnDrawAction"
        draw_event_lt = self.window.scribbleArea.Loads(str(pb.draw_action))
        self.window.scribbleArea.LoadDrawEvent(draw_event_lt)


    def LoginFail(self, pb):
        if pb.response == pb.FAIL_SERVER_FULL:
            self.window.Critical(u"服务器人数已满！")

        elif pb.response == pb.FAIL_SYSTEM_ERROR:
            self.window.Critical(u"系统错误！")

        elif pb.response == pb.FAIL_INVALID_CLIENT_VERSION:
            self.window.Critical(u"新版本已发布。请重新进入频道进行升级。")

        else:
            self.window.Critical(u"未知错误。")

        self.ForceClose()


    def OnLoginMainResponse(self, pb):
        print "OnLoginMainResponse", pb.response
        print "My name uid", pb.uid, #pb.name
        if pb.response != pb.OK:
            return self.LoginFail(pb)

        self.SetUidName(pb.uid, pb.name)
        self.uid = pb.uid
        self.yy_name = pb.name
        self.chl_name = pb.channel_name
        self.chl_id = pb.channel_id
        self.short_chl_id = pb.shortchannel_id

        self.InitGameInfo(pb)
        self.connection.GetUserInfo(self.OnGetUserInfo)
        self.StartPing()
        self.OnLoginMainSucessful()


    def OnLoginMainSucessful(self):
        self.word_mgr.CreateWordWindow()
        self.standard_mgr.score_window.CheckAuthority()


    def OnRemoveDrawerList(self, pb):
        print "OnRemoveDrawerList"
        for uid in pb.uid:
            if self.game_mode == draw_pb2.STANDRAD_TURN:
                self.window.observer_list.SetPlayerOffline(uid)
                self.window.player_list.OnPlayerLeave(uid)
            else:
                self.window.player_list.OnPlayerLeave(uid)
                self.window.observer_list.OnPlayerLeave(uid)
            if self.uid_name.has_key(uid):
                del self.uid_name[uid]


    def ShowTip(self, text):
        self.window.label_keyword.setText(text)
        #self.window.AnimateMidTip(True)
        #self.SetTimer(TIP_INTERVAL, self.OnShowTipTimer, True)


    def OnShowTipTimer(self):
        self.window.AnimateMidTip(False)


    def SetPlayer(self):
        pass


    def SetObserver(self):
        pass


    def SetMyGameRole(self, role):
        print "SetMyGameRole", role
        self.game_role = role

        if role == WATCHER_ROLE:
            self.window.HideDrawToolButton()
            self.window.button_draw.show()
            self.window.button_ob.hide()

            if self.cur_host_uid:
                self.EnterWatcherState()
            else:
                self.EnterRestState()
        else:
            self.window.button_draw.hide()
            self.window.button_ob.show()

            if role == PLAYER_ROLE:
                self.EnterPlayerState()
            elif role == DRAWING_ROLE:
                self.EnterDrawingState()


    def SetOtherGameRole(self, role):
        pass


    def SetGameRole(self, uid, role):
        print "set game role ", uid
        if self.uid == uid:
            self.SetMyGameRole(role)
        else:
            self.SetOtherGameRole(role)

        if role == WATCHER_ROLE:
            self.window.player_list.OnPlayerLeave(uid)
            self.window.observer_list.OnPlayerEnter(uid, self.GetUsrName(uid))
        else:
            self.window.observer_list.OnPlayerLeave(uid)
            self.window.player_list.OnPlayerEnter(uid, self.GetUsrName(uid))


    def SetMeHost(self, is_tip):
        print "SetMeHost"
        self.window.scribbleArea.is_host = True
        self.ResetDrawToolButton()
        self.window.ShowDrawToolButton()
        if is_tip:
            self.ShowTip(u"该你画啦!!!")
        self.window.button_draw.setEnabled(False)
        self.EnterDrawingState()


    def SetNoHost(self):
        print "SetNoHost"
        self.EnterRestState()


    def SetOtherHost(self):
        print "SetOtherHost"
        self.EnterWatcherState()


    def SetHost(self, uid, is_tip=True):
        print "game-SetHost", uid, self.uid
        self.cur_host_uid = uid
        self.window.player_list.SetHost(uid)

        if uid == self.uid:
            self.SetMeHost(is_tip)
            return 
        
        self.window.scribbleArea.is_host = False
        if uid == 0:
            self.SetNoHost()
        else:
            self.SetOtherHost()



    def OnSetHost(self, pb):
        print "OnSetHost", pb.drawer_id
        self.Countdown(pb.round_second)
        self.SetHost(pb.drawer_id)


    def ResetDrawToolButton(self):
        self.window.button_black.click()
        self.window.button_scri.click()
        self.window.button_small.click()


    # 右键菜单
    def OnPopMenuTriggerd(self, uid, pop_idx):
        if pop_idx == POP_MENU_SET_HOST:
            self.RequestSetHost(uid)
        elif pop_idx == POP_MENU_SET_OB:
            self.RequestSetOb(uid)
        elif pop_idx == POP_MENU_TALK_TO:
            self.chat_mgr.SetTalkTo(uid)
        else:
            self.RequestGetDetail(uid)


    # 设置别人为主笔
    def RequestSetHost(self, uid):
        print "RequestSetHost", uid
        self.RequestSetGameRole(uid, DRAWING_ROLE)


    # 设置别人为旁观
    def RequestSetOb(self, uid):
        print "RequestSetOb", uid
        self.RequestSetGameRole(uid, WATCHER_ROLE)


    # 点击加入按钮
    def RequestJoin(self):
        if self.game_mode == draw_pb2.STANDRAD_TURN:
            self.standard_mgr.ThrowDice()
        else:
            self.RequestBeHost()


    # 自己申请加入主笔队列
    def RequestBeHost(self):
        self.RequestSetGameRole(self.uid, PLAYER_ROLE)


    # 自己加入旁观者
    def RequestBeObserver(self):
        self.RequestSetGameRole(self.uid, WATCHER_ROLE)


    def EnterRootChannel(self):
        print "EnterRootChannel"
        self.LoginMain(UNIVERSAL_TOP_CHANNEL_HALL)


    def EnterChildChannel(self):
        print "EnterChildChannel"
        self.LoginMain(INDIVIDUAL_CHANNEL_ROOM)


    def OnGetScoreResponse(self, pb):
        print "OnGetScoreResponse", pb.response_type, pb.target_type
        if pb.response_type != pb.OK:
            return

        if pb.target_type == TARGET_SELF:
            # 更新鲜花鸡蛋道具数
            self.appraise_panel.OnSetMyItemAmount(pb.flower_amount, pb.egg_amount)
            self.my_card.Update(pb)
        elif pb.target_type == TARGET_MASTER_DRAWER:
            print "get host detail"
            self.host_card.Update(pb)
        else:
            print "get uid detail"
            self.detail_card.Update(pb.target_uid, pb)


    def RequestGetDetail(self, uid):
        print "RequestGetDetail"
        pb = dc2ds_get_score_request()
        pb.target_type = TARGET_UID
        pb.target_uid = uid
        self.connection.SendPb(pb)

    
    def UploadPic(self):
        ret = QtGui.QMessageBox.question(self.window, g_title, u"确定要上传吗？", u"确定", u"取消", "", 1)
        if ret != 0:
           return

        upload_file = "%s%s" % (DECODEGB1(sys.executable)[:-3], "png")
        self.window.scribbleArea.saveImage(upload_file, u"png")

        def OnUploading():
            print "OnUploading"
            self.window.button_upload.setDisabled(True)

        def OnUploadFinised():
            print "OnUploadFinised"
            self.chat_mgr.ShowAnnounce(u"上传成功")
            def OnTimer():
                self.window.button_upload.setDisabled(False)
            self.SetTimer(UPLOAD_INTERVAL, OnTimer, True)

        def OnUploadError():
            print "upload error"
            self.window.button_upload.setDisabled(False)
            self.chat_mgr.ShowAnnounce(u"上传错误")

        self.upload_module = GetUploadMgr()
        self.upload_module.AddCallbacks(OnUploading, OnUploadError, OnUploadFinised)
        keyword = self.standard_mgr.GetKeyword()
        self.upload_module.on_upload_triggar(self.uid, self.chl_id, self.chl_id, self.yy_name, keyword, upload_file, self.short_chl_id)
        


