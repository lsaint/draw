# -*- coding:utf-8 -*-
'''
    author: lSaint
    date: 2011-10-14
    desc: 评价道具使用面板

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''


from draw_pb2 import *
from common import *


class AppraisePanel(object):

    def __init__(self, window, game):
        self.item_dict = {OBJ_CATEGORY_FLOWER:0, OBJ_CATEGORY_EGG:0}
        self.window = window
        self.game = game
        self.connection = game.connection
        self.Hide()

        self.CreateConnection()


    def SetItemAmount(self, item_type, amount):
        self.item_dict[item_type] = amount
        if item_type == OBJ_CATEGORY_FLOWER:
            self.window.label_item_xh.setText(unicode(amount))
        elif item_type == OBJ_CATEGORY_EGG:
            self.window.label_item_jd.setText(unicode(amount))


    def OnSetMyItemAmount(self, flower_num, egg_num):
        print "OnSetMyItemAmount", flower_num, egg_num
        self.SetItemAmount(OBJ_CATEGORY_FLOWER, flower_num)
        self.SetItemAmount(OBJ_CATEGORY_EGG, egg_num)


    def OnGainItemNotification(self, pb):
        print u"获得道具", pb.uid, pb.item_type, pb.amount
        if pb.uid != self.game.uid:
            return
        self.SetItemAmount(pb.item_type, pb.amount)
        self.game.chat_mgr.ShowAnnounce(GAIN_ITEM_TIP[pb.item_type])


    def Show(self):
        print self.item_dict
        if self.item_dict[OBJ_CATEGORY_FLOWER] > 0:
            self.window.button_use_xh.setDisabled(False)
        else:
            self.window.button_use_xh.setDisabled(True)

        if self.item_dict[OBJ_CATEGORY_EGG] > 0:
            self.window.button_use_jd.setDisabled(False)
        else:
            self.window.button_use_jd.setDisabled(True)

        self.window.label_xh_used.setText(u"0")
        self.window.label_jd_used.setText(u"0")
        self.window.button_use_xh.setChecked(False)
        self.window.button_use_jd.setChecked(False)
        self.window.widget_item_use.show()


    def Hide(self):
        self.window.widget_item_use.hide()


    def Reset(self):
        self.window.label_xh_used.setText(u"0")
        self.window.label_jd_used.setText(u"0")
        self.window.button_use_xh.setChecked(False)
        self.window.button_use_jd.setChecked(False)


    def RegisterItemPannelCallback(self):
        self.connection.AddHandler(ds2dc_gain_item_notification, self.OnGainItemNotification)
        self.connection.AddHandler(ds2dc_use_item_notification, self.OnUseItemNotification)
        self.connection.AddHandler(ds2dc_use_item_response, self.OnUseItemResonse)


    def CreateConnection(self):
        self.window.button_use_xh.toggled.connect(self.UseItemFlowser)
        self.window.button_use_jd.toggled.connect(self.UseItemEgg)


    def UseItem(self, item_type):
        self.window.button_use_xh.setDisabled(True)
        self.window.button_use_jd.setDisabled(True)

        pb = dc2ds_use_item_request()
        pb.target_type = TARGET_MASTER_DRAWER
        pb.item_type = item_type
        pb.amount = 1
        self.connection.SendPb(pb)
        print "dc2ds_use_item_request"


    def UseItemFlowser(self, used):
        if not used:
            return

        if self.item_dict[OBJ_CATEGORY_FLOWER] <= 0:
            self.game.chat_mgr.ShowAnnounce(u"鲜花数量不足。")
            self.window.button_use_xh.setDisabled(True)
            return

        self.UseItem(OBJ_CATEGORY_FLOWER)


    def UseItemEgg(self, used):
        if not used:
            return

        if self.item_dict[OBJ_CATEGORY_EGG] <= 0:
            self.game.chat_mgr.ShowAnnounce(u"鸡蛋数量不足。")
            self.window.button_use_jd.setDisabled(True)
            return 
        
        self.UseItem(OBJ_CATEGORY_EGG)


    def OnUseItemNotification(self, pb):
        print "OnUseItemNotification"
        self.AddAppriseItem(pb.item_type, pb.amount)
        self.ShowAppriseTip(pb.uid, pb.target_uid, pb.item_type)


    def AddAppriseItem(self, item_type, amount):
        if item_type == OBJ_CATEGORY_FLOWER:
            label = self.window.label_xh_used
        else:
            label = self.window.label_jd_used

        num = int(label.text())
        label.setText(unicode(num + amount))


    def ReduceItemAmount(self, item_type):
        self.SetItemAmount(item_type, self.item_dict[item_type]-1)


    def OnUseItemResonse(self, pb):
        print "OnUseItemResonse"
        if pb.response_type == pb.FAIL_THIS_ITEM_CAN_NOT_USE_ON_SELF:
            self.game.chat_mgr.ShowAnnounce(u"不能对自己使用。")
        elif pb.response_type == pb.FAIL_ERROR_TARGET:
            self.game.chat_mgr.ShowAnnounce(u"错误对象。")
        elif pb.response_type == pb.FAIL_ERROR_ITEM_TYPE: 
            self.game.chat_mgr.ShowAnnounce(u"错误道具")
        elif pb.response_type == pb.FAIL_ERROR_NOT_ENOUGTH_AMOUNT:
            self.game.chat_mgr.ShowAnnounce(u"数量不足")
        elif pb.response_type == pb.FAIL_ERROR_STATE:
            self.game.chat_mgr.ShowAnnounce(u"错误状态")
        else:
            self.AddAppriseItem(pb.item_type, pb.amount)
            self.ReduceItemAmount(pb.item_type)
            self.ShowAppriseTip(0, pb.target_uid, pb.item_type)


    def ShowAppriseTip(self, uid_s, uid_t, item_type):                            
        name_s = self.game.GetUsrName(uid_s)
        name_t = self.game.GetUsrName(uid_t)

        if item_type == OBJ_CATEGORY_FLOWER:
            if uid_s == 0:
                tip = u"你向%s出一束%s" % (name_t, FLOWER_COLOR_NAME)
            else:
                tip = u"%s向%s送出一束%s"% (name_s, name_t, FLOWER_COLOR_NAME )
        else:
            if uid_s == 0:
                tip = u"你向%s扔出一个%s" %( name_t, EGG_COLOR_NAME )
            else:
                tip = u"%s向%s扔出一个%s"% (name_s, name_t, EGG_COLOR_NAME )
        
        self.game.chat_mgr.ShowSystemTip(tip)


