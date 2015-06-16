# -*- coding:utf-8 -*-
'''
    file: scribble.py
    author: lSaint
    date: 2011-06-16
    desc: 你画我猜 涂鸦

    广州华多网络科技有限公司 版权所有 (c) 2005-2010 DuoWan.com [多玩游戏]
'''

from PyQt4 import QtCore, QtGui
from pickle_event import *


DRAW_STATE_SCRI = 1 # 涂鸦
DRAW_STATE_RECT = 2 # 矩形
DRAW_STATE_ELLI = 3 # 圆形

TRANSPARENCY  = QtGui.qRgba(255,255,255,0)
WHITE = QtGui.qRgb(255, 255, 255)



class ScribbleArea(QtGui.QWidget, ScribblePickle):
    def __init__(self, parent=None):
        super(ScribbleArea, self).__init__(parent)
        ScribblePickle.__init__(self)

        self.setAttribute(QtCore.Qt.WA_StaticContents)
        # 保存标示
        self.modified = False
        self.erase_color = QtCore.Qt.white
        self.image = QtGui.QImage()
        # 快速图形工具预览
        self.preview_image = QtGui.QImage()
        self.lastPoint = QtCore.QPoint()
        # 主笔标记
        self.is_host = False
        self.Reset()


    def Reset(self):
        # 涂鸦中
        self.scribbling = False
        # 当前画笔
        self.cur_width = 3
        self.cur_color = QtCore.Qt.black
        # 绘画画笔
        self.draw_width = 3
        self.draw_color = QtCore.Qt.black
        # 擦除画笔
        self.erase_width = 6
        # 绘画状态
        self.draw_state = DRAW_STATE_SCRI
        self.image.fill(WHITE)
        self.preview_image.fill(TRANSPARENCY)




    def PickleScribbleEvent(self, event):
        if not self.is_host:
            return
        return ScribblePickle.PickleScribbleEvent(self, event)


    def saveImage(self, fileName, fileFormat):
        visibleImage = self.image
        self.resizeImage(visibleImage, self.size(), False)

        if visibleImage.save(fileName, fileFormat):
            self.modified = False
            return True
        else:
            return False


    def setPenColor(self, newColor):
        self.draw_color = newColor


    def setPenWidth(self, newWidth):
        self.draw_width = newWidth


    def clearImage(self):
        self.PickleScribbleEvent(ClearEvent())
        self.image.fill(WHITE)
        self.preview_image.fill(TRANSPARENCY)
        self.modified = False
        self.update()


    def SetCurAction(self, event, action): 
        self.lastPoint = event.pos()

        if action == QtCore.Qt.RightButton: 
            self.cur_width = self.draw_width+2 # 橡皮擦略大
            self.cur_color = self.erase_color
        else:
            self.cur_width = self.draw_width
            self.cur_color = self.draw_color

        self.PickleScribbleEvent(ColorEvent(self.cur_color))
        self.PickleScribbleEvent(WidthEvent(self.cur_width))
        self.PickleScribbleEvent(MPressEvent((event.pos().x(), event.pos().y())))
       
        if self.draw_state == DRAW_STATE_SCRI or\
                action == QtCore.Qt.RightButton:
            self.scribbling = True
            self.preview_image.fill(TRANSPARENCY)
            self.update()
   

    def mousePressEvent(self, event):
        if not self.is_host:
            return

        if event.button() == QtCore.Qt.RightButton:
            self.SetCurAction(event, QtCore.Qt.RightButton)
        if event.button() == QtCore.Qt.LeftButton:
            self.SetCurAction(event, QtCore.Qt.LeftButton)


    def mouseMoveEvent(self, event):
        if not self.is_host:
            return

        if (event.buttons() & QtCore.Qt.LeftButton) and self.scribbling:
            self.scribbleTo(event.pos())

        if (event.buttons() & QtCore.Qt.RightButton) and self.scribbling:
            self.scribbleTo(event.pos())

        if (event.buttons() & QtCore.Qt.LeftButton) and not self.scribbling:
            self.drawPreview(event.pos())

        
    def mouseReleaseEvent(self, event):
        if (event.button() == QtCore.Qt.LeftButton or event.button() == QtCore.Qt.RightButton)\
                and self.is_host:
            if self.scribbling:
                self.scribbleTo(event.pos())
                self.PickleScribbleEvent(MReleaseEvent((event.pos().x(), event.pos().y())))
                self.scribbling = False
            else:
                self.preview_image.fill(TRANSPARENCY)
                self.drawPatternTo(self.image, event.pos(), True)


    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(self.image.rect(), self.image)
        painter.drawImage(self.preview_image.rect(), self.preview_image)


    def scribbleTo(self, endPoint):
        self.PickleScribbleEvent(PointEvent((endPoint.x(), endPoint.y())))
        painter = QtGui.QPainter(self.image)
        painter.setPen(QtGui.QPen(self.cur_color, self.cur_width,
                QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawLine(self.lastPoint, endPoint)
        self.modified = True

        rad = self.cur_width/ 2 + 2
        self.update(QtCore.QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
        self.lastPoint = QtCore.QPoint(endPoint)


    # 快速图形
    def drawPatternTo(self, image, point2, is_pickle):
        path = QtGui.QPainterPath()
        if self.draw_state == DRAW_STATE_RECT:
            rect = QtCore.QRectF(QtCore.QPointF(self.lastPoint), QtCore.QPointF(point2))
            path.addRect(rect)
            if is_pickle:
                self.PickleScribbleEvent(RectEvent(self.lastPoint, point2))
        elif self.draw_state == DRAW_STATE_ELLI:
            elli =  QtCore.QRectF(QtCore.QPointF(self.lastPoint), QtCore.QPointF(point2))
            path.addEllipse(elli)
            if is_pickle:
                self.PickleScribbleEvent(ElliEvent(self.lastPoint, point2))

        painter = QtGui.QPainter(image)
        painter.setPen(QtGui.QPen(self.cur_color, self.cur_width,
                            QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        painter.drawPath(path)
        self.update()


    # 快速图形预览
    def drawPreview(self, point2):
        self.preview_image.fill(TRANSPARENCY)
        self.drawPatternTo(self.preview_image, point2, False)


    def LoadDrawEvent(self, lt):
        length = len(lt)
        print "recv len", length
        for event in lt:
            if event.__class__ == ColorEvent:
                self.cur_color = event.color
            elif event.__class__ == WidthEvent:
                self.cur_width = event.width
            elif event.__class__ == MPressEvent:
                self.lastPoint = QtCore.QPoint(*event.point)
                self.scribbling = True
            elif event.__class__ == MReleaseEvent:
                self.scribbleTo(QtCore.QPoint(*event.point))
                self.scribbling = False
            elif event.__class__ == ClearEvent:
                self.clearImage()
            elif event.__class__ == PointEvent:
                self.scribbleTo(QtCore.QPoint(*event.point))
            elif event.__class__ == DrawStateEvent:
                self.draw_state = event.state
            elif event.__class__ == RectEvent:
                self.drawPatternTo(self.image, event.bottom_right, False)
            elif event.__class__ == ElliEvent:
                self.drawPatternTo(self.image, event.bottom_right, False)
            else:
                print event.__class__
                raise "Load ERROR scribble event"


    def resizeImage(self, image, newSize, for_preview_image=True):
        if image.size() == newSize:
            return

        newImage = QtGui.QImage(newSize, QtGui.QImage.Format_RGB32)
        newImage.fill(WHITE)
        painter = QtGui.QPainter(newImage)
        painter.drawImage(QtCore.QPoint(0, 0), image)
        self.image = newImage
        
        if not for_preview_image:
            return
        newImage = QtGui.QImage(newSize, QtGui.QImage.Format_ARGB32)
        newImage.fill(TRANSPARENCY)
        painter = QtGui.QPainter(newImage)
        painter.drawImage(QtCore.QPoint(0, 0), image)
        self.preview_image = newImage


    def isModified(self):
        return self.modified


    def penColor(self):
        return self.draw_color


    def penWidth(self):
        return self.draw_width


    def SetScriState(self):
        self.PickleScribbleEvent(DrawStateEvent(DRAW_STATE_SCRI))
        self.draw_state = DRAW_STATE_SCRI


    def SetElliState(self):
        self.PickleScribbleEvent(DrawStateEvent(DRAW_STATE_ELLI))
        self.draw_state = DRAW_STATE_ELLI


    def SetRectState(self):
        self.PickleScribbleEvent(DrawStateEvent(DRAW_STATE_RECT))
        self.draw_state = DRAW_STATE_RECT

