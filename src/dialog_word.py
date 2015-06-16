# -*- coding:utf-8 -*-
'''
    file: dialog_sumit.py
    author: lSaint
    date: 2011-08-29
    desc: 上传窗口 

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''


from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QDialog
from common import *
from ui_word import Ui_dialog_word
import draw_pb2
from draw_pb2 import *



class WordWindow(QDialog, Ui_dialog_word):

    def __init__(self, parent, game):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(g_title)
        self.game = game
        self.word_mgr = game.word_mgr
        self.tmp_word_chl = ""

        self.button_edit.toggled.connect(self.OnEditButtonToggled)
        self.button_edit_apply.clicked.connect(self.UpdateChlWord)
        self.button_sumit_sys.clicked.connect(self.SumitSysWord)
        self.button_sumit_chl.clicked.connect(self.SumitChlWord)

        self.CheckAuthority()


    def CheckAuthority(self):
        for widget in (self.word_edit_chl, self.button_sumit_chl, self.button_edit):
            widget.setEnabled(self.game.IsAdmin())


    def GetChlEditWords(self):
        return self.word_edit_chl.toPlainText().split("\n")


    def GetSysEditWords(self):
        return self.word_edit_sys.toPlainText().split("\n")


    def ShowSysTip(self, msg):
        self.label_ret_sys.setText(msg)


    def ShowChlTip(self, msg):
        self.label_ret_chl.setText(msg)


    def UpdateChlWord(self):
        print "UpdateChlWord"
        new_words = self.GetChlEditWords()
        if new_words == self.tmp_word_chl:
            return 
        self.word_mgr.RequestUpdateChannelWords(new_words)
        self.word_edit_chl.clear()
        self.tmp_word_chl = ""

        self.button_edit_apply.setDisabled(True)
        self.button_edit.setChecked(False)


    def SumitChlWord(self):
        self.word_mgr.RequestSumitChlWords(self.GetChlEditWords())
        self.label_ret_chl.setText(u"成功提交至频道词库")
        self.word_edit_chl.clear()
        self.tmp_word_chl = ""


    def SumitSysWord(self):
        if self.word_mgr.RequestSumitSysWords(self.GetSysEditWords()):
            self.label_ret_sys.setText(u"提交成功，感谢您的参与")
            self.word_edit_sys.clear()


    def OnEditButtonToggled(self, flag):
        self.word_edit_chl.clear()

        # 弹起
        if not flag:
            self.button_edit_apply.setDisabled(True)
            self.button_sumit_chl.setDisabled(False)
            return

        # 按下
        self.label_ret_chl.clear()
        self.button_edit_apply.setDisabled(False)
        self.button_sumit_chl.setDisabled(True)

        #if not self.tmp_word_chl:
        self.word_mgr.RequestShowChlWords()

        #print "get from tmp"
        #for w in self.tmp_word_chl:
        #    self.word_edit_chl.appendPlainText(w)


    def OnShowChlWords(self, words):
        self.tmp_word_chl = words
        for w in words:
            self.word_edit_chl.appendPlainText(w)


    def hide(self):
        super(WordWindow, self).hide()
        self.tmp_word_chl = ""
    

    def Show(self):
        self.word_edit_sys.clear()
        self.word_edit_chl.clear()
        self.label_ret_chl.clear()
        self.label_ret_sys.clear()
        self.button_edit.setChecked(False)

        self.show()


#
#import sys
#
#if __name__ == '__main__':
#    app = QtGui.QApplication(sys.argv)
#    window = WordWindow()
#    window.show()
#    sys.exit(app.exec_())




