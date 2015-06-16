# -*- coding:utf-8 -*-
'''
    author: lSaint
    date: 2011-10-13
    desc: 通用窗口 父类 (无系统边框，顶部区域可拖动窗口)

    广州华多网络科技有限公司 版权所有 (c) 2005-2010 DuoWan.com [多玩游戏]
'''

from PyQt4 import QtCore, QtGui
from common import *


class CommonWindow(object):

    def __init__(self):
        self.moving = False
        self.last_mouse_pos = None
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)


    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and event.y() < MAX_DRAG_Y_COORDINATE:
            self.moving = True 
            self.last_mouse_pos = event.globalPos() 


    def mouseMoveEvent(self, event):
        if (event.buttons() & QtCore.Qt.LeftButton) and self.moving:
            self.move(self.pos() + (event.globalPos() - self.last_mouse_pos)) 
            self.last_mouse_pos = event.globalPos() 


    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton: 
            self.moving = False 

