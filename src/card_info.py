# -*- coding:utf-8 -*-
'''
    author: lSaint
    date: 2011-10-20
    desc: 玩家名片，主笔名片，详细信息名片

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''


from PyQt4.QtGui import QCursor
from PyQt4 import QtGui


# 父类
class CardInfo(object):

    def __init__(self):
        self.draw_be_hitted_amount = 0
        self.hitted_amount = 0
        self.good_item_amount = 0
        self.bad_item_amount = 0
        self.first_hitted_amount = 0
        self.master_draw_amount = 0
        self.round_amount = 0
        self.flower_amount = 0
        self.egg_amount = 0


    def SetDetailedInfo(self, pb):
        self.draw_be_hitted_amount = pb.draw_be_hitted_amount
        self.hitted_amount = pb.hitted_amount
        self.good_item_amount = pb.good_item_amount
        self.bad_item_amount = pb.bad_item_amount
        self.first_hitted_amount = pb.first_hitted_amount
        self.master_draw_amount = pb.master_draw_amount
        self.round_amount = pb.round_amount
        self.flower_amount = pb.flower_amount
        self.egg_amount = pb.egg_amount




# 详细资料
class DetailedCard(CardInfo):


    def __init__(self, window, game):
        super(DetailedCard, self).__init__()
        self.window = window
        self.game = game
        self.timer = None

        self.window.widget_detailed_card.hide()
        self.window.widget_detailed_card.sig_mouse_leave.connect(self.Hide)
        self.window.widget_detailed_card.sig_mouse_enter.connect(self.StopTimer)


    def Show(self):
        pos = self.window.mapFromGlobal(QCursor.pos())
        self.window.widget_detailed_card.move(pos.x()-10, pos.y()-10)
        self.window.widget_detailed_card.show()


    def Hide(self):
        self.timer = self.game.SetTimer(400, self.window.widget_detailed_card.hide, True)


    def StopTimer(self):
        if self.timer  and self.timer.isActive():
            self.timer.stop()


    def Update(self, uid, pb):
        self.SetDetailedInfo(pb)

        self.window.label_det_name.setText(self.game.GetUsrName(uid))
        self.window.label_det_byz.setText(unicode(pb.draw_be_hitted_amount))
        self.window.label_det_yz.setText(unicode(pb.hitted_amount))
        self.window.label_det_xh.setText(unicode(pb.good_item_amount))
        self.window.label_det_jd.setText(unicode(pb.bad_item_amount))
        self.window.label_det_sz.setText(unicode(pb.first_hitted_amount))
        self.window.label_det_zbs.setText(unicode(pb.master_draw_amount))
        self.window.label_det_zjs.setText(unicode(pb.round_amount))

        watcher_amount = float(pb.round_amount-pb.master_draw_amount)
        if watcher_amount <= 0:
            rate = u"0.0%"
        else:
            rate = "%.1f%%" % (pb.first_hitted_amount*100/watcher_amount)
        self.window.label_det_szl.setText(rate)

        self.Show()




LIST_SHOW = 1
LINE_SHOW = 2


# 主笔名片
class HostCard(CardInfo):

    def __init__(self, game, window):
        super(HostCard, self).__init__()
        self.game = game
        self.button_extern = window.button_extern
        self.card = window.widget_host_card
        self.player_list = window.player_list
        self.label_host_jd = window.label_host_jd
        self.label_host_xh = window.label_host_xh
        self.mark = window.widget_mouse_mark_host
        #self.show_as = LINE_SHOW

        self.button_extern.toggled.connect(self.Extern)
        self.mark.sig_mouse_enter.connect(self.ShowHostDetail)


    def Reset(self):
        self.label_host_xh.clear()
        self.label_host_jd.clear()


    def ShowHostDetail(self):
        if self.game.cur_host_uid != 0 :
            self.game.detail_card.Update(self.game.cur_host_uid, self)



    def ShowAsList(self):
        print "ShowAsList"
        #self.show_as = LIST_SHOW
        self.card.setStyleSheet(u"#widget_host_card {\n"
"    border-image: url(:/image/drawer_list.png);\n"
"}")
        self.label_host_jd.hide()
        self.label_host_xh.hide()
        self.player_list.setGeometry(self.player_list.x(), self.player_list.y(),\
                    self.player_list.width(), 61)
        self.player_list.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.card.setGeometry(self.card.x(), self.card.y(), 284, 79)
        self.mark.hide()


    def ShowAsLine(self):
        print "ShowAsLine"
        #self.show_as = LINE_SHOW
        self.card.setStyleSheet(u"#widget_host_card {\n"
"    border-image: url(:/image/card.png);\n"
"}")
        self.player_list.setGeometry(self.player_list.x(), self.player_list.y(),\
                    self.player_list.width(), 21)
        self.player_list.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.label_host_jd.show()
        self.label_host_xh.show()
        self.card.setGeometry(self.card.x(), self.card.y(), 340, 73)
        self.mark.show()


    def Show(self):
        print "show host card"
        self.card.show()
        self.button_extern.setChecked(True)


    def Hide(self):
        print "hide host card"
        self.Reset()
        self.card.hide()
        self.button_extern.setChecked(False)


    def Extern(self, e):
        if e:
            self.card.show()
        else:
            self.card.hide()


    def Update(self, pb):
        print "Update host card"
        self.label_host_jd.setText(unicode(pb.bad_item_amount))
        self.label_host_xh.setText(unicode(pb.good_item_amount))

        self.SetDetailedInfo(pb)




# 自己名片
class MyCard(CardInfo):

    def __init__(self, game, window):
        super(MyCard, self).__init__()
        self.window = window
        self.game = game

        self.window.label_add_xh.hide()
        self.window.label_add_jd.hide()
        self.window.label_add_sz.hide()
        self.window.label_add_yz.hide()
        self.window.label_add_byz.hide()

        self.window.widget_mouse_mark_mine.sig_mouse_enter.connect(self.ShowMyDetail)

        self.is_first = True


    def ShowMyDetail(self):
        self.game.detail_card.Update(self.game.uid, self)


    def Update(self, pb):
        #print ""
        #print "draw_be_hitted_amount", pb.draw_be_hitted_amount
        #print "hitted_amount", pb.hitted_amount
        #print "good_item_amount", pb.good_item_amount
        #print "bad_item_amount", pb.bad_item_amount
        #print "first_hitted_amount", pb.first_hitted_amount
        #print "master_draw_amount", pb.master_draw_amount
        #print "round_amount", pb.round_amount
        #print "flower_amount", pb.flower_amount
        #print "egg_amount", pb.egg_amount

        self.window.label_total_xh.setText(unicode(pb.good_item_amount))
        self.window.label_total_jd.setText(unicode(pb.bad_item_amount))

        def template(old, new, label_add, label_inc):
            num = new - old
            if num > 0:
                label_add.show()
                label_inc.setText(unicode(num))
            else:
                label_add.hide()
                label_inc.clear()

        if self.is_first:
            self.is_first = False
            self.SetDetailedInfo(pb)
            return

        template(self.good_item_amount, pb.good_item_amount, self.window.label_add_xh, self.window.label_inc_xh)
        template(self.bad_item_amount, pb.bad_item_amount, self.window.label_add_jd, self.window.label_inc_jd)
        template(self.first_hitted_amount, pb.first_hitted_amount, self.window.label_add_sz, self.window.label_inc_sz)
        template(self.hitted_amount, pb.hitted_amount, self.window.label_add_yz, self.window.label_inc_yz)
        template(self.draw_be_hitted_amount, pb.draw_be_hitted_amount, self.window.label_add_byz, self.window.label_inc_byz)
        self.SetDetailedInfo(pb)

