# -*- coding:utf-8 -*-
'''
    file: dialog_score.py
    author: lSaint
    date: 2011-08-15
    desc: 标准模式分数显示窗口

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''


from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QDialog
from ui_score import Ui_score_dialog
from common import *
from style_sheet import *
from common_window import CommonWindow
from datetime import datetime


class ScoreWindow(QDialog, Ui_score_dialog, CommonWindow):

    def __init__(self, game, parent=None): 
        QDialog.__init__(self, parent)
        CommonWindow.__init__(self)
        self.game = game
        self.connection = game.connection
        self.setupUi(self)
        self.move(SCORE_WINDOW_POS)
        self.setWindowTitle(g_title)
        self.score_table.verticalScrollBar().setStyleSheet(sh_scroll_v)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.Reset()
        self.CreateConnection()
        self.button_stop.hide()
        self.hide()


    def Reset(self):
        self.recording = False
        self.cur_row = 0
        self.score_table.setColumnWidth(0, 182) # 人名
        self.score_table.setColumnWidth(1, 40)  # 首中
        self.score_table.setColumnWidth(2, 40)  # 歪中
        self.score_table.setColumnWidth(4, 55)  # 累计首中
        self.score_table.setColumnWidth(5, 55)  # 累计歪中
        self.score_table.setColumnWidth(6, 45)  # 鲜花
        self.score_table.setColumnWidth(7, 45)  # 鸡蛋
        self.score_table.clearContents()
        self.last_time = self.box_last_time.value()
        self.label_stop_time.clear()


    def Clear(self):
        print "clear score list _)__________"
        self.score_table.clearContents()
        self.cur_row = 0


    def CheckAuthority(self):
        for widget in (self.button_stop, self.button_start, self.box_last_time):
            widget.setEnabled(self.game.IsAdmin())


    def CreateConnection(self):
        self.button_start.clicked.connect(self.RequestStartRecord)
        self.button_stop.clicked.connect(self.RequestStopRecord)
        self.box_last_time.valueChanged.connect(self.EditLastTime)


    def RegisterScoreCallback(self):
        self.connection.AddHandler(dc2ds_start_action_request, self.OnStartRecordResponse)
        self.connection.AddHandler(ds2dc_start_action_response, self.OnStartRecordResponse)
        self.connection.AddHandler(ds2dc_start_action_notification, self.OnStartRecordNotification)
        self.connection.AddHandler(ds2dc_stop_action_response, self.OnStopRecordResponse)
        self.connection.AddHandler(ds2dc_stop_action_notification, self.OnStopRecordNotification)
        self.connection.AddHandler(ds2dc_chn_action_score_notification, self.OnGetScoreList)


    def EditLastTime(self, i):
        self.last_time = i
        print "edit last_time", self.last_time
        
    
    def SetShowTimer(self):
        timer =  QtCore.QTimer(self)
        timer.singleShot(10000, self.OnShowTimer)


    def OnShowTimer(self):
        self.close()


    def Show(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()


    def AutoShow(self):
        if self.isVisible():
            return
        self.show()
        self.SetShowTimer()


    def AddLine(self, uid, usr_name, is_first, is_hit, total_be_hit, total_first_hit, total_hit, flower_num, egg_num):
        name = self.game.GetUsrName(uid)
        if name == "":
            name = usr_name
        if self.score_table.rowCount() > self.cur_row:
            row = self.cur_row
        else:
            row = self.score_table.rowCount()
            self.score_table.insertRow(row)
        self.cur_row += 1
        item0 = QtGui.QTableWidgetItem(name)
        item0.setToolTip(name)
        item1 = QtGui.QTableWidgetItem(("", u"√")[is_first])
        item2 = QtGui.QTableWidgetItem(("", u"√")[is_hit])
        item3 = QtGui.QTableWidgetItem((u"%d"%total_be_hit).rjust(MAX_DICE_COUNT))
        item4 = QtGui.QTableWidgetItem((u"%d"%total_first_hit).rjust(MAX_DICE_COUNT))
        item5 = QtGui.QTableWidgetItem((u"%d"%total_hit).rjust(MAX_DICE_COUNT))
        item6 = QtGui.QTableWidgetItem((u"%d"%flower_num).rjust(MAX_DICE_COUNT))
        item7 = QtGui.QTableWidgetItem((u"%d"%egg_num).rjust(MAX_DICE_COUNT))
        for i in range(8):
            item = eval("item%d"%i)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.score_table.setItem(row, i, item)


    def GetTime(sefl, sec):
        print datetime.fromtimestamp(sec).isoformat()
        return unicode(datetime.fromtimestamp(sec).isoformat().replace("T", " "))


    def RequestStartRecord(self):
        print "StartRecord", self.last_time
        pb = dc2ds_start_action_request()
        pb.duration = self.last_time
        self.connection.SendPb(pb)


    def OnStartRecordResponse(self, pb):
        print "OnStartRecordResponse"
        if pb.response_type == pb.OK:
            return

        if pb.response_type == pb.FAIL_DURATION_ERROR:
            tip = u"记录持续事件错误。"
        elif pb.response_type == pb.FAIL_ERROR_OP_AUTHORITY:
            tip = u"你没有权限。"
        elif pb.response_type == pb.FAIL_STARTED_ALREADY:
            tip = u"积分正在记录中。"
        self.game.chat_mgr.ShowAnnounce(tip)

        #FAIL_DURATION_ERROR
        #FAIL_ERROR_OP_AUTHORITY
        #FAIL_STARTED_ALREADY
        #self.SetButtonState(True)
        #endtime = self.GetTime(pb.end_time)
        #self.game.chat_mgr.ShowAnnounce(u"设置成功, 开始记录积分。结束时间为%s。" % endtime)
        #self.label_stop_time.setText(endtime)
        #self.Clear()


    def OnStartRecordNotification(self, pb):
        print "OnStartRecordNotification"
        name = self.game.GetUsrName(pb.operation_uid)
        if name == "":
            name = pb.operation_name

        end_time = u"结束时间: %s" % self.GetTime(pb.end_time)
        last_time = (pb.end_time-pb.start_time)/60
        
        self.game.chat_mgr.ShowAnnounce(u"%s开启了积分记录。持续%d分钟，%s。" % (name, last_time, end_time))
        self.label_stop_time.setText(end_time)
        self.box_last_time.setValue(last_time)
        self.SetButtonState(True)
        self.Clear()


    def OnStopRecordResponse(self, pb):
        print "OnStopRecordResponse"
        if pb.response_type != pb.OK:
            return

        #self.SetButtonState(False)
        #self.game.chat_mgr.ShowAnnounce(u"积分记录已停止。")
        #self.AutoShow()
        #self.label_stop_time.clear()


    def OnStopRecordNotification(self, pb):
        print "OnStopRecordNotification"
        if pb.operation_uid == 0:
            tip = u"积分记录已停止。"
        else:
            name = self.game.GetUsrName(pb.operation_uid)
            if name == "":
                name = pb.operation_name
            tip = u"%s提前结束了积分记录。" % name
        self.label_stop_time.clear()
        self.SetButtonState(False)
        self.game.chat_mgr.ShowAnnounce(tip)
        self.AutoShow()


    def RequestStopRecord(self):
        print "StopRecord"
        pb = dc2ds_stop_action_request()
        self.connection.SendPb(pb)


    def SetButtonState(self, is_start):
        self.button_stop.setVisible(is_start)
        self.button_start.setVisible (not is_start)
        self.box_last_time.setDisabled(is_start)
        print "set box disable", is_start


    def OnGetScoreList(self, pb):
        print "::::::::::::;;wOnGetScoreList"
        self.Clear()
        for us in pb.user_score_list:
            print us.uid, us.first_hit_this_round, us.hit_this_round, us.draw_be_hitted_amount
            self.AddLine(us.uid, us.name, us.first_hit_this_round, us.hit_this_round, us.draw_be_hitted_amount,\
                    us.first_hitted_amount, us.hitted_amount, us.good_item_amount, us.bad_item_amount)


