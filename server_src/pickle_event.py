# -*- coding:utf-8 -*-
'''
    file: pickle_event.py
    author: lSaint
    date: 2011-06-16
    desc: 你画我猜 系列化事件

    广州华多网络科技有限公司 版权所有 (c) 2005-2010 DuoWan.com [多玩游戏]
'''

import cPickle, zlib



# 系列化
class ScribblePickle(object):

    def __init__(self):
        self.event_list = []


    def PickleScribbleEvent(self, event_data):
        self.event_list.append(event_data)


    def Dumps(self):
        if self.event_list == []:
            return None
        s = cPickle.dumps(self.event_list)
        print "dumps len", len(s)
        c = zlib.compress(s, 9)
        print "zlib len", len(c)
        self.event_list = []
        return c


    def Loads(self, data):
        return cPickle.loads(zlib.decompress(data))


    def TestDump(self):
        f = open("pickle.pi", "wb")
        cPickle.dump(self.event_list, f)
        self.event_list = []
        f.close()
        print "test dump over"


    def TestLoad(self):
        f = open("pickle.pi", "rb")
        s = cPickle.load(f)
        f.close()
        print "test load over"
        return s


# 涂鸦事件基类
class ScribbleEvent(object):

    pass
    #SE_POINT = 1
    #SE_COLOR = 2
    #SE_WIDTH = 3
    #SE_CLEAR = 4
    #SE_MPRESS = 5
    #SE_MRELEASE = 6
    #
    #event_type  = 0

    #def GetType(self):
    #    return self.event_type 


# 画点事件
class PointEvent(ScribbleEvent):

    #event_type = ScribbleEvent.SE_POINT

    def __init__(self, point):
        self.point = point



# 换颜色事件
class ColorEvent(ScribbleEvent):

    #event_type = ScribbleEvent.SE_COLOR

    def __init__(self, color):
        self.color = color



# 换笔宽事件
class WidthEvent(ScribbleEvent):

    #event_type = ScribbleEvent.SE_WIDTH

    def __init__(self, width):
        self.width = width


# 鼠标压下
class MPressEvent(ScribbleEvent):

    #event_type = ScribbleEvent.SE_MPRESS

    def __init__(self, point):
        self.point = point 



# 鼠标抬起
class MReleaseEvent(ScribbleEvent):

    #event_type = ScribbleEvent.SE_MRELEASE

    def __init__(self, point):
        self.point = point



# 清空事件
class ClearEvent(ScribbleEvent):

    #event_type = ScribbleEvent.SE_CLEAR
    pass


# 
class DrawStateEvent(ScribbleEvent):

    def __init__(self, s):
        self.state = s


# 矩形
class RectEvent(ScribbleEvent):

    def __init__(self, p1, p2):
        self.top_left = p1
        self.bottom_right = p2


# 椭圆
class ElliEvent(ScribbleEvent):

    def __init__(self, p1, p2):
        self.top_left = p1
        self.bottom_right = p2




