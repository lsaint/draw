# -*- coding:utf-8 -*-
'''
    file: launcher.py
    author: lSaint
    date: 2011-09-29
    desc: 启动窗口

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''


import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QDialog
from ui_launcher import Ui_launcher
from common import *
from common_window import CommonWindow
from style_sheet import *

from web_token import WebToken
from web_panel import *
from web_common import WebCommon

class Launcher(QDialog, Ui_launcher, CommonWindow):

    def __init__(self, parent=None): 
        super(Launcher, self).__init__()
        #QDialog.__init__(self, parent)
        CommonWindow.__init__(self)
        self.setupUi(self)
        self.setWindowTitle(g_title)
        self.chl_list.verticalScrollBar().setStyleSheet(sh_scroll_v)

        self.game = None
        
        self._webtoken = WebToken()
        self._picture_web_panel = WebPanel(self)
        self._picture_web_panel.setGeometry(QtCore.QRect(292, 54, 689,483))
        #self._picture_web_panel.setStyleSheet(u"border: none;")
        self._info_web_panel = WebPanel(self)
        self._info_web_panel.setGeometry(QtCore.QRect(22, 54, 257, 204))
        #self._info_web_panel.setStyleSheet(u"background-color: transparent;")

        
    def CreateConnection(self):
        self.button_enter_root.clicked.connect(self.game.EnterRootChannel)
        self.button_enter_child.clicked.connect(self.game.EnterChildChannel)
    

    def LoadInfoWebPage(self):
        self._info_web_panel.setUrl(WebCommon.INFO_WEB_URL)
    
    def LoadPictureWebPage(self,topchannel_id):
        self._picture_web_panel.setUrlByChannelId(topchannel_id)
        

    def OnLoginLauncherResponse(self, pb):
        print "OnLoginLauncherResponse"
        if pb.response != pb.OK:
            self.game.LoginFail(pb)
            return

        self.label_chl_info.setText(u"%s(%d)" % (pb.channel_name, pb.topchannel_id))
        self.label_name.setText(u"<font color='black'>%s</font>" % pb.name)

        self.LoadPictureWebPage(pb.topchannel_id)
        self.LoadInfoWebPage()

        self.chl_list.clear()
        for rf in pb.active_room_list:
            suf = "(%d)" % rf.user_amount
            pre = rf.room_name
            try:
                str(pre)
            except:
                cut_len_pre = MAX_LAUNCHER_ROOM_NAME/2 - len(suf)
            else:
                cut_len_pre = MAX_LAUNCHER_ROOM_NAME - len(suf)
            # 半个中文字符问题
            cut_len_pre = (cut_len_pre, cut_len_pre+1)[cut_len_pre%2]
            if len(pre) > cut_len_pre:
                pre = "%s%s" % (pre[:cut_len_pre], "...")
                print "len pre", len(pre)
            ret = u"%s%s" % (pre, suf)
            #print ret, len(ret)
            item = QtGui.QListWidgetItem(ret)
            item.setToolTip(rf.room_name)
            self.chl_list.addItem(item)


#app = QtGui.QApplication(sys.argv)
#w = Launcher()
#w.show()
#sys.exit(app.exec_())    

