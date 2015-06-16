# -*- coding: utf-8 -*-
'''
    file: qt_class.py
    author: lSaint
    date: 2011-06-24
    desc: 你画我猜 Qt控件自定义类 

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''


from PyQt4 import QtGui, QtCore
from common import *
from style_sheet import *


# 自绘按钮
class QPaintButton(QtGui.QPushButton):

    def __init__(self, parent=None):
        super(QPaintButton, self).__init__(parent)
        self.pen_width = 0 


    def paintEvent(self, event):
        QtGui.QPushButton.paintEvent(self, event)
        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush(QtCore.Qt.SolidPattern)
        painter.setBrush(brush)
        point = QtCore.QPoint(self.width()/2, self.height()/2)
        painter.drawEllipse(point, self.pen_width, self.pen_width)



# 去掉table内item选中时的虚线框
class NoFocusDelegate(QtGui.QStyledItemDelegate):

    def paint(self, painter, option, index):
        itemOption = QtGui.QStyleOptionViewItem(option)
        if (itemOption.state & QtGui.QStyle.State_HasFocus):
            itemOption.state = itemOption.state ^ QtGui.QStyle.State_HasFocus
        QtGui.QStyledItemDelegate.paint(self, painter, itemOption, index)



# 长的像list的table
# 托管玩家列表控件的显示 带右键菜单
class QTableListWidget(QtGui.QTableWidget):

    uid_selected = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):
        super(QTableListWidget, self).__init__(parent)
        self.uid_item = {}
        self.host_uid = None
        self.setItemDelegate(NoFocusDelegate())
    
        self.menu = PopMenu(self)
        self.menu.ConnectTalkToAction(self.OnTalkTo)
        self.menu.ConnectSetHostAction(self.OnSelectHost)
        self.menu.ConnectSetObAction(self.OnSetOb)
        self.menu.ConnectGetDetailAction(self.OnGetDetail)

        self.horizontalScrollBar().setStyleSheet(sh_scroll_h)
        self.verticalScrollBar().setStyleSheet(sh_scroll_v)


    def GetUids(self):
        return self.uid_item.keys()


    # 自定义类型的初始化，在setupUi之后
    def Init(self, label):
        self.label_num = label
        self.setColumnWidth(COL_NAME, LEN_COL_NAME)
        self.setColumnWidth(COL_DICE, LEN_COL_DICE)


    def GetCurRowNameItem(self):
        if self.currentRow() >= 0:
            return self.item(self.currentRow(), COL_NAME)


    def GetItemsByUid(self, uid):
        item = self.uid_item.get(uid)
        if item is None:
            return (None, None)
        row = self.row(item)
        return (self.item(row, COL_NAME), self.item(row, COL_DICE))


    def SetDice(self, uid, num):
        print "SetDice"
        item = self.GetItemsByUid(uid)[COL_DICE]
        if not item:
            return
        item.setText(unicode(num).rjust(MAX_DICE_COUNT))


    def SetAuthority(self, b):
        self.menu.is_admin = b


    def UpdatePlayerNum(self):
        self.label_num.setText(u"%d" % len(self.uid_item))


    def OnPlayerEnter(self, uid, name):
        if self.uid_item.get(uid) is not None:
            return# self.SetBackgroundColor(uid, QtCore.Qt.transparent)
            
        item_name  = QtGui.QTableWidgetItem(name)
        item_name.setToolTip(name)
        item_name.uid = uid
        item_dice = QtGui.QTableWidgetItem()
        row = self.rowCount()
        self.uid_item[uid] = item_name
        self.insertRow(row)
        self.setItem(row, COL_NAME, item_name)
        self.setItem(row, COL_DICE, item_dice)
        self.UpdatePlayerNum()


    def OnPlayerLeave(self, uid):
        print "OnPlayerLeave", uid
        if uid is self.host_uid:
            self.host_uid = None
        item = self.uid_item.get(uid)
        if item is None:
            return
        row = self.row(item)
        self.removeRow(row)
        del self.uid_item[uid]
        self.UpdatePlayerNum()


    # 当玩家在roll点后离开游戏时会有该状态显示,否则直接OnPlayerLeave
    def SetPlayerOffline(self, uid):
        _, dice_item = self.GetItemsByUid(uid)
        if not dice_item:
            return
        if dice_item.text() != "":
            dice_item.setBackgroundColor(OFFLINE_BACKGROUND_COLOR)
        else:
            self.OnPlayerLeave(uid)


    # 清空所有玩家扔的点数并撤掉离线玩家
    def Shuffle(self):
        for uid in self.uid_item.keys():
           _, ditem = self.GetItemsByUid(uid) 
           if not ditem:
               continue
           if ditem.backgroundColor() == OFFLINE_BACKGROUND_COLOR:
               self.removeRow(self.row(ditem))
               del self.uid_item[uid]
           else:
               ditem.setText("")


    def Clear(self):
        self.uid_item = {}
        #self.clear()
        count = self.rowCount()
        while(count>=0):
           self.removeRow(0) 
           count -= 1


    def SetBackgroundColor(self, uid, color):
        for i in self.GetItemsByUid(uid):
            if i:
                i.setBackgroundColor(color)


    def SetHost(self, uid):
        if not self.uid_item.get(uid):
            return 
        self.SetBackgroundColor(self.host_uid, QtCore.Qt.transparent)
        self.host_uid = uid 
        # 只有一行时不加底色
        if self.rowCount() != 1:
            self.SetBackgroundColor(uid, HOST_BACKGROUND_COLOR)


    # 在列表中选择一位主笔(主持模式)
    def OnSelectHost(self):
        print " OnSelectHost"
        item = self.GetCurRowNameItem()
        if item is not None:
            self.uid_selected.emit(item.uid, POP_MENU_SET_HOST)


    def OnTalkTo(self):
        print "OnTalkTo"
        item = self.GetCurRowNameItem()
        if item is not None:
            self.uid_selected.emit(self.currentItem().uid, POP_MENU_TALK_TO)


    def OnSetOb(self):
        print "set ob"
        item = self.GetCurRowNameItem()
        if item is not None:
            self.uid_selected.emit(self.currentItem().uid, POP_MENU_SET_OB)


    def OnGetDetail(self):
        item = self.GetCurRowNameItem()
        if item is not None:
            self.uid_selected.emit(self.currentItem().uid, POP_MENU_GET_DETAIL)


    def contextMenuEvent(self, event):
        print "contextMenuEvent"
        item = self.GetCurRowNameItem()
        if item is not None:
            self.menu.Pop()





class  PopMenu(object):

    def __init__(self, parent):
        self.is_admin = False
        self.pop_menu = QtGui.QMenu(parent)

        self.action_get_detail = QtGui.QAction(u"查看详细信息", parent)
        self.pop_menu.addAction(self.action_get_detail)

        self.action_talk = QtGui.QAction(u"私聊", parent)
        self.pop_menu.addAction(self.action_talk)

        self.action_set_host = QtGui.QAction(u"设为主笔", parent)
        self.pop_menu.addAction(self.action_set_host)

        self.action_set_ob = QtGui.QAction(u"设为围观", parent)
        self.pop_menu.addAction(self.action_set_ob)


    def ConnectSetHostAction(self, slot):
        self.action_set_host.triggered.connect(slot)
        

    def ConnectTalkToAction(self, slot):
        self.action_talk.triggered.connect(slot)


    def ConnectSetObAction(self, slot):
        self.action_set_ob.triggered.connect(slot)


    def ConnectGetDetailAction(self, slot):
        self.action_get_detail.triggered.connect(slot)
        

    def Pop(self):
        if self.is_admin:
            self.action_set_host.setDisabled(False)
            self.action_set_ob.setDisabled(False)
        else:
            self.action_set_host.setDisabled(True)
            self.action_set_ob.setDisabled(True)

        self.pop_menu.exec_(QtGui.QCursor.pos())
    


# 响应任意鼠标键点击超链接的TextBrowser
class QChatMsgBrowser(QtGui.QTextBrowser):

    # 带超链接的鼠标点击信号
    name_clicked = QtCore.pyqtSignal(unicode, int)

    def mousePressEvent(self, event):
        url_data = self.anchorAt(event.pos())
        if url_data != "":
            self.name_clicked.emit(url_data, event.button())   
        return super(QChatMsgBrowser, self).mousePressEvent(event)



# 带历史记录的聊天栏
class QHistoryLineEdit(QtGui.QLineEdit):

    MAX_SAVE = 50

    def __init__(self, parent=None):
        super(QHistoryLineEdit, self).__init__(parent)
        self.history = []
        self.cursor = -1
        self.tmp_save = ""


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            print "upppp", self.cursor
            if self.cursor+1 >= len(self.history):
                print "return", self.cursor, len(self.history), self.history
                return
            if self.cursor == -1:
                self.tmp_save = self.text()
            self.cursor += 1
            self.setText(self.history[self.cursor])

        elif event.key() == QtCore.Qt.Key_Down:
            print "downnn", self.cursor
            if self.cursor-1 < 0:
                print "return"
                self.cursor = -1
                self.setText(self.tmp_save)
                return
            self.cursor -= 1
            self.setText(self.history[self.cursor])

        super(QHistoryLineEdit, self).keyPressEvent(event)


    def SaveHistory(self):
        if self.text() == "":
            print "save return"
            return
        print "save", self.text()
        if len(self.history) ==  self.MAX_SAVE:
            self.history.pop()
        self.history.insert(0, self.text())
        self.cursor = -1



class Billboard(QtGui.QLabel):

    def __init__(self, parent=None):
        super(Billboard, self).__init__(parent)

        self.text_list = []
        self.counter = 0
        self.length = 0

        #self.timer = QtCore.QTimer(self)
        #self.timer.timeout.connect(self.OnChangeText)
        #self.timer.start(15000)
        self.connect(self, QtCore.SIGNAL('clicked()'), self.OnChangeText) 


    def AddText(self, text):
        self.text_list.append(text)
        if self.counter == 0:
            self.setText(text)
        self.length += 1


    def OnChangeText(self):
        if self.text_list:
            text = self.text_list[self.counter % self.length]
            self.setText(text) 
            self.counter += 1


    def mouseReleaseEvent(self, ev):  
        self.emit(QtCore.SIGNAL('clicked()'))  



# 扑捉鼠标进入离开的并发出signal的widget
class DetailedTipWidget(QtGui.QWidget):

    sig_mouse_enter = QtCore.pyqtSignal()
    sig_mouse_leave = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(DetailedTipWidget, self).__init__(parent)
        self.detailed = None

    
    def enterEvent(self, event):
        self.sig_mouse_enter.emit()


    def leaveEvent(self, event):
        self.sig_mouse_leave.emit()


    def paintEvent(self, event):
        super(DetailedTipWidget, self).paintEvent(event)
        opt = QtGui.QStyleOption() 
        opt.init(self)
        p = QtGui.QPainter(self) 
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, p, self); 



