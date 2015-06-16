# -*- coding:utf-8 -*-
'''
    file: animate.py
    author: lSaint
    date: 2011-09-01
    desc: 动画管理

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''



from PyQt4 import QtCore, QtGui
from ui import Ui_MainWindow


class AnimationFrame(QtGui.QMainWindow, Ui_MainWindow):

    sig_arrow_animate = QtCore.pyqtSignal()
    sig_midtip_animate = QtCore.pyqtSignal()
    hold_list = []

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)

        self.InitArrowAnimation()
        self.InitMidTipAnimation()


    def InitMidTipAnimation(self):
        self.NormalInitAnimation(self.label_tip, self.sig_midtip_animate,\
                  geometry_s = QtCore.QRect(500, 25, 141, 21))
                  #curve = QtCore.QEasingCurve.InOutQuint)


    def InitArrowAnimation(self):
        self.NormalInitAnimation(self.label_arrow, self.sig_arrow_animate,\
              geometry_s = QtCore.QRect(self.label_arrow.x(), self.label_arrow.y()+600,\
                        self.label_arrow.width(), self.label_arrow.height()))


    def NormalInitAnimation(self, widget, signal, **argv):
        machine = QtCore.QStateMachine()
        group = QtCore.QParallelAnimationGroup()

        self.hold_list.append(signal)
        self.hold_list.append(group)
        self.hold_list.append(machine)

        duration = argv.get("duration", 3000)
        curve  = argv.get("curve", QtCore.QEasingCurve.OutElastic)
        geometry_s = argv.get("geometry_s", widget.geometry())
        geometry_e = argv.get("geometry_e", widget.geometry())

        #self.group_p = QtCore.QParallelAnimationGroup()

        goe = QtGui.QGraphicsOpacityEffect()
        widget.setGraphicsEffect(goe)
        animation_o = QtCore.QPropertyAnimation(goe, "opacity")
        animation_g = QtCore.QPropertyAnimation(widget, "geometry")

        animation_g.setDuration(duration)
        animation_g.setEasingCurve(curve)
        animation_o.setDuration(duration)

        group.addAnimation(animation_g)
        group.addAnimation(animation_o)

        #self.machine = QtCore.QStateMachine()
        state1 = QtCore.QState(machine)
        state1_1 = QtCore.QState(state1)
        state1_2 = QtCore.QState(state1)
        state2 = QtCore.QState(machine)
        machine.setInitialState(state1)
        state1.setInitialState(state1_1)

        state1_1.assignProperty(widget, "geometry", geometry_s)
        state1_1.assignProperty(goe, "opacity", 0.1)
        state1_2.assignProperty(widget, "visible", False)
        state1_1.addTransition(state1_1.propertiesAssigned, state1_2)

        state2.assignProperty(widget, "geometry", geometry_e)
        state2.assignProperty(widget, "visible", True)
        state2.assignProperty(goe, "opacity", 1)

        transition = state1.addTransition(signal, state2)
        transition.addAnimation(group)

        transition = state2.addTransition(signal, state1)
        transition.addAnimation(group)
        machine.start()


    def NormalAnimate(self, signal, widget, is_show):
        if is_show and not widget.isVisible():
            return signal.emit()
            
        if not is_show and widget.isVisible():
            return signal.emit()


    def AnimateArrow(self, is_show):
        print " AnimateArrow"
        self.NormalAnimate(self.sig_arrow_animate, self.label_arrow, is_show)

     
    def AnimateMidTip(self, is_show):
        print " AnimateMidTip"
        self.NormalAnimate(self.sig_midtip_animate, self.label_tip, is_show)
        


