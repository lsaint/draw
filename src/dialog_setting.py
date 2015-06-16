# -*- coding:utf-8 -*-
'''
    file: dialog_setting.py
    author: lSaint
    date: 2011-08-03
    desc: 设置窗口 

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

from PyQt4.QtGui import QDialog
from PyQt4 import QtCore
from ui_setting import Ui_setting_dialog
from common import *


class SettingWindow(QDialog, Ui_setting_dialog):

    def __init__(self, parent, game):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(g_title)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.game = game
        self.chat_mgr = game.chat_mgr
        
        self.box_game_mode.currentIndexChanged.connect(self.OnGameModeChanged)
        self.box_talk_mode.currentIndexChanged.connect(self.OnTalkModeChanged)
        self.box_interval.editingFinished.connect(self.OnChatIntervalChanged)
        self.box_chlword_rate.currentIndexChanged.connect(self.OnChlWordRateChanged)

        self.button_applly.clicked.connect(self.OnApply)
        self.button_cancel.clicked.connect(self.OnClose)
        self.button_confirm.clicked.connect(self.OnConfirm)
        self.Reset()


    def Reset(self):
        self.tmp_game_mode = self.game.game_mode
        self.tmp_talk_mode = self.chat_mgr.talk_mode
        self.tmp_interval = self.chat_mgr.chat_interval
        self.tmp_chlword_rate = self.game.word_mgr.chlword_rate


    def OnApply(self):
        if self.game.game_mode != self.tmp_game_mode:
            self.game.RequestSetGameMode(self.tmp_game_mode)

        if self.chat_mgr.talk_mode != self.tmp_talk_mode:
            self.chat_mgr.RequestConfigTalkMode(self.tmp_talk_mode)

        if self.chat_mgr.chat_interval != self.tmp_talk_mode:
            self.chat_mgr.RequestSetChatInterval(self.tmp_interval)

        if self.game.word_mgr.chlword_rate != self.tmp_chlword_rate:
            self.game.word_mgr.RequestSetChlWordRate(self.tmp_chlword_rate)


    def OnClose(self):
        self.Reset()
        self.hide()


    def OnConfirm(self):
        self.OnApply()
        self.hide()


    def OnGameModeChanged(self, idx):
        self.tmp_game_mode = UI_GAME_MODE_R[idx]


    def OnTalkModeChanged(self, idx):
        self.tmp_talk_mode = UI_TALK_MODE_R[idx]


    def OnChatIntervalChanged(self):
        self.tmp_interval = self.box_interval.value()


    def OnChlWordRateChanged(self, idx):
        self.tmp_chlword_rate = UI_CHL_WORD_RATE_R[idx]


    def Show(self):
        self.box_game_mode.setCurrentIndex(UI_GAME_MODE[self.game.game_mode])
        self.box_talk_mode.setCurrentIndex(UI_TALK_MODE[self.chat_mgr.talk_mode])
        self.box_interval.setValue(self.chat_mgr.chat_interval)
        self.box_chlword_rate.setCurrentIndex(UI_CHL_WORD_RATE[self.game.word_mgr.chlword_rate])
        self.show()




