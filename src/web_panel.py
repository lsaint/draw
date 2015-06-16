# -*- coding:utf-8 -*-
'''
    file: web_panel.py
    author: alanxzj
    date: 2011-10-25
    desc: web页面面板

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''


import sys
#from PyQt4 import QtCore, QtGui, QtWebKit
from PyQt4 import QtCore, QtGui, QAxContainer
from PyQt4.QtGui import QDialog
from common import *

from web_token import WebToken
from web_common import WebCommon

#class WebPanel(QtWebKit.QWebView):
class WebPanel(QAxContainer.QAxWidget):
    def __init__(self, parent=None): 
        super(WebPanel, self).__init__(parent)
        self._webtoken = WebToken()
        self.InitWebConfig()
        
    def InitWebConfig(self):
        #self.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, True)
        #self.settings().setAttribute(QtWebKit.QWebSettings.JavaEnabled, True)
        #self.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
        #self.settings().setAttribute(QtWebKit.QWebSettings.JavascriptCanOpenWindows, True)
        #self.settings().setAttribute(QtWebKit.QWebSettings.PrivateBrowsingEnabled,True)        
        #self.settings().setAttribute(QtWebKit.QWebSettings.AutoLoadImages,True)
        #self.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setControl("{8856F961-340A-11D0-A96B-00C04FD705A2}")
        self.setObjectName("web_panel")
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

    def setUrlByChannelId(self,topchannel_id):
        url = "%stopchn=%d&webtoken=%s" % (WebCommon.PICTURE_WEB_URL, topchannel_id, self._webtoken.index_encode("%d"%topchannel_id))
        self.setUrl(url)

    def setUrl(self, url):
        self.dynamicCall('Navigate(const QString&)', url)
        print url
        #self.dynamicCall('Navigate(const QString&)', "http://172.16.42.30/draw/topchn=2080&webtoken=9b81886d6b594c5c2b19720144c105ad")
