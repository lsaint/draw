
# -*- coding:utf-8 -*-
'''
    file: dialog_help.py
    author: lSaint
    date: 2011-08-01
    desc: 帮助窗口

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

from PyQt4.QtGui import QDialog
from ui_help import Ui_help_dialog
from common import *
from style_sheet import *
from common_window import CommonWindow


class HelpWindow(QDialog, Ui_help_dialog, CommonWindow):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        CommonWindow.__init__(self)
        self.move(HELP_WINDOW_POS)
        self.setupUi(self)
        self.setWindowTitle(g_title)
        self.textBrowser.verticalScrollBar().setStyleSheet(sh_scroll_v)



