# -*- coding:utf-8 -*-
'''
    author: lSaint
    date: 2011-06-16
    desc: 你画我歪 游戏主界面

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

from PyQt4 import QtCore, QtGui
from scribble import ScribbleArea
from style_sheet import *
from common import *
from dialog_help import HelpWindow
from dialog_setting import SettingWindow
from animate import AnimationFrame
from common_window import CommonWindow


# 主窗口
class GuessWindow(AnimationFrame, CommonWindow):

    def __init__(self):
        print "__init__ guess"
        super(GuessWindow, self).__init__()
        CommonWindow.__init__(self)
        self.scribbleArea = ScribbleArea(self.size_widget)
        c_size = self.size_widget.size()
        self.scribbleArea.resize(c_size)
        self.scribbleArea.resizeImage(self.scribbleArea.image, c_size)
       
        self.HideSomething()

        self.msg_view.document().setDefaultStyleSheet(href_style)
        self.box_talk_target.insertSeparator(3)

        self.player_list.Init(self.player_num)
        self.observer_list.Init(self.observer_num)

        # test
        #self.scribbleArea.is_host = True 
        #self.setting = SettingWindow(self, self)
        #self.player_list.OnPlayerEnter(1, u"11111")
        #self.player_list.OnPlayerEnter(2, u"22222")
      
       
    def ShowMessage(self, text):
        self.label_announce.setText(text)


    def HideSomething(self):
        self.label_tip.hide()
        #self.label_arrow.hide()
        self.player_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.observer_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.HideDrawToolButton()
        self.player_num.hide()
        self.button_draw.hide()
        self.button_ob.hide()
        #self.label_keyword.hide()
        #self.host_card.Hide()


    def HideDrawToolButton(self):
        for button in self.pen_color_group.buttons()\
                + self.pen_width_group.buttons()\
                + self.draw_tool_group.buttons():
            button.hide()
        self.button_clear.hide()
        self.button_upload.hide()


    def ShowDrawToolButton(self):
        for button in self.pen_color_group.buttons()\
                + self.pen_width_group.buttons()\
                + self.draw_tool_group.buttons():
            button.show()
        self.button_clear.show()
        self.button_upload.show()


    def CreateSaveFormat(self):
        for fm in QtGui.QImageWriter.supportedImageFormats():
            fm = str(fm)
            text = fm.upper()
            action = QtGui.QAction(text, self, triggered=self.Save)
            action.setData(fm)
            self.save_menu.addAction(action)


    def OnRecvData(self, data):
        draw_event_lt = self.scribbleArea.Loads(data)
        self.scribbleArea.LoadDrawEvent(draw_event_lt)


    def SetPenColor(self):
        newColor = QtGui.QColorDialog.getColor(self.scribbleArea.penColor())
        if newColor.isValid():
            self.scribbleArea.setPenColor(newColor)


    def SetPenWidth(self):
        dialog = QtGui.QInputDialog(self)
        dialog.setWindowTitle(g_title)
        dialog.setOkButtonText(u"确定")
        dialog.setCancelButtonText(u"取消")
        dialog.setLabelText(u"选择大小:")
        dialog.setIntRange(1, 30)
        dialog.setIntValue(self.scribbleArea.penWidth())
        if (dialog.exec_() == QtGui.QDialog.Accepted):
            newWidth = dialog.intValue()
            self.scribbleArea.setPenWidth(newWidth)


    def CreateConnection(self):
        self.connect(self.clear, QtCore.SIGNAL('triggered()'), self.ClearImage)
        self.connect(self.button_clear, QtCore.SIGNAL('clicked()'), self.ClearImage)
        
        self.connect(self.pen_color, QtCore.SIGNAL('triggered()'), self.SetPenColor)
        #self.connect(self.button_color, QtCore.SIGNAL('clicked()'), self.SetPenColor)

        self.connect(self.pen_width, QtCore.SIGNAL('triggered()'), self.SetPenWidth)
        #self.connect(self.button_width, QtCore.SIGNAL('clicked()'), self.SetPenWidth)

        self.connect(self.exit, QtCore.SIGNAL('triggered()'), self.close)
        self.connect(self.about, QtCore.SIGNAL('triggered()'), self.About)

        self.button_close.clicked.connect(self.close)
        self.button_min.clicked.connect(self.showMinimized)

        self.button_big.clicked.connect(self.SetBigPen)
        self.button_small.clicked.connect(self.SetSmallPen)
        self.button_normal.clicked.connect(self.SetNormalPen)

        self.button_yellow.toggled.connect(self.SetColorYellow)
        self.button_black.toggled.connect(self.SetColorBlack)
        self.button_blue.toggled.connect(self.SetColorBlue)
        self.button_red.toggled.connect(self.SetColorRed)
        self.button_green.toggled.connect(self.SetColorGreen)
        self.button_eraser.toggled.connect(self.SetColorWhite)
        
        self.player_list.uid_selected.connect(self.game.OnPopMenuTriggerd)
        self.observer_list.uid_selected.connect(self.game.OnPopMenuTriggerd)
        self.button_draw.clicked.connect(self.game.RequestJoin)
        self.button_ob.clicked.connect(self.game.RequestBeObserver)

        self.button_help.clicked.connect(self.OnHelp)
        self.button_setting.clicked.connect(self.OnSetting)

        self.button_save.clicked.connect(self.DefaultSave)

        self.button_sumit.clicked.connect(self.OnSumit)

        self.button_rect.toggled.connect(self.scribbleArea.SetRectState)
        self.button_elli.toggled.connect(self.scribbleArea.SetElliState)
        self.button_scri.toggled.connect(self.scribbleArea.SetScriState)

        self.button_back.clicked.connect(self.game.BackToLauncher)
        self.button_upload.clicked.connect(self.game.UploadPic)


    def ClearImage(self):
        if self.scribbleArea.is_host:
            self.scribbleArea.clearImage()


    def SetSmallPen(self):
        self.scribbleArea.setPenWidth(PEN_SMALL)


    def SetBigPen(self):
        self.scribbleArea.setPenWidth(PEN_BIG)


    def SetNormalPen(self):
        self.scribbleArea.setPenWidth(PEN_NORMAL)


    def SetColorGreen(self):
        self.scribbleArea.setPenColor(GREEN)


    def SetColorBlack(self):
        self.scribbleArea.setPenColor(BLACK)


    def SetColorBlue(self):
        self.scribbleArea.setPenColor(BLUE)


    def SetColorRed(self):
        self.scribbleArea.setPenColor(RED)


    def SetColorYellow(self):
        self.scribbleArea.setPenColor(YELLOW)


    def SetColorWhite(self):
        self.scribbleArea.setPenColor(WHITE)
        self.button_scri.click()


    def About(self):
        QtGui.QMessageBox.about(self, g_title, "L'")


    def Save(self):
        action = self.sender()
        fileFormat = action.data()
        self.SaveFile(fileFormat)
       

    def closeEvent(self, event):
        #if self.MaybeSave():
        #    event.accept()
        #    self.game.LogoutMain()
        #else:
        #    event.ignore()
        self.game.LogoutMain()


    def Critical(self, text):
        QtGui.QMessageBox.critical(self, g_title, text, u"确定")


    def MaybeSave(self):
        if self.scribbleArea.isModified():
            ret = QtGui.QMessageBox.warning(self, g_title,
                        u"画图已被修改.\n你希望保存吗?",
                        u"直接退出", u"取消", u"保存后退出")
            if ret == 2: 
                return self.SaveFile()
            elif ret == 1:
                return False

        return True


    def SaveFile(self, fileFormat=u"png"):
        initialPath = g_title + "." + fileFormat

        fileName = QtGui.QFileDialog.getSaveFileName(self, u"保存为", initialPath,
                u"%s 文件(*.%s);;所有文件 (*)" % (fileFormat.upper(), fileFormat))
        if fileName:
            return self.scribbleArea.saveImage(fileName, fileFormat)

        return False


    def DefaultSave(self):
        self.SaveFile()
            

    def OnHelp(self):
        hw = HelpWindow(self)
        hw.show()
        print self.player_list.geometry()


    def OnSetting(self):
        if not hasattr(self, "setting"):
            self.setting  = SettingWindow(self, self.game)
        self.setting.move(self.x()+10, self.y()+250)
        self.setting.Show()


    def OnSumit(self):
        if hasattr(self.game.word_mgr, "dialog_word"):
            self.game.word_mgr.dialog_word.Show()


    def ResetUI(self):
        self.player_list.Clear()
        self.observer_list.Clear()
        self.scribbleArea.Reset()



#if __name__ == '__main__':
#    app = QtGui.QApplication(sys.argv)
#    window = GuessWindow()
#    window.show()
#    sys.exit(app.exec_())


