# -*- coding:utf-8 -*-

import MultipartPostHandler, cookielib, urllib2
from PyQt4 import QtCore, QtGui
from web_token import WebToken
from web_common import WebCommon

class UploadWorker(QtCore.QThread):

    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self._uid = ''
        self._chn = ''
        self._topchn = ''
        self._shortchn = ''
        self._keyword = ''
        self._name = ''
        self._uploadpicture = None

    #def __del__(self):
    #    self.wait()

    def upload_picture(self, uid, chn, topchn, shortchn, keyword, name, path, webtoken):
        self._uid = uid
        self._chn = chn
        self._topchn = topchn
        self._shortchn = shortchn
        self._keyword = keyword
        self._name = name
        try:
            self._uploadpicture = open(path, "rb")
        except IOError:
            return False
            
        self._webtoken = webtoken
        self.start()
        return True

    def run(self):      
        params = {'uid': self._uid, 'chn': self._chn, 'topchn': self._topchn, 'shortchn':self._shortchn, 'keyword':self._keyword, 'name':self._name, 'webtoken':self._webtoken, 'uploadpicture': self._uploadpicture }
        cookies = cookielib.CookieJar()
        for key in params:
            print key, params[key], type(params[key])
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies), MultipartPostHandler.MultipartPostHandler)
        try:
            res = opener.open(WebCommon.UPLOAD_IMAGES_ABS_URL_BASE, params, 10)
        except:
            print "upload error"
        return


def Finished():
    GetUploadMgr().finished()


def Terminated():
    GetUploadMgr().terminated()


        
class UploadMgr(QtGui.QWidget):
    def __init__(self,):
        self._webtoken = WebToken()
        self._thread = UploadWorker()

        self.connect(self._thread, QtCore.SIGNAL("finished()"), Finished)
        self.connect(self._thread, QtCore.SIGNAL("terminated()"), Terminated)

        self.uploading_callback = None
        self.terminated_callback = None
        self.finished_callback = None


    def AddCallbacks(self, up, ter, fi):
        self.uploading_callback = up
        self.terminated_callback = ter
        self.finished_callback = fi

        
    def on_upload_triggar(self, uid, chn, topchn, name, keyword, filename, short_chl_id):
        #for debug
        #uid = "88888888"
        #chn = "5000000"
        #topchn = "2080"
        #name = "亚亚"
        #keyword = "keyword"
        #filename = "sns.png"
        
        webtoken = self._webtoken.upload_encode(uid,chn,topchn).encode("utf-8")
        if not self._thread.upload_picture(unicode(uid).encode("utf-8"), unicode(chn).encode("utf-8"), unicode(topchn).encode("utf-8"), unicode(short_chl_id).encode("utf-8"), keyword.encode("utf-8"), name.encode("utf-8"), filename.encode("utf-8"), webtoken ):
            return False
        self.uploading_callback()
        return True
        
       
    def finished(self):
        print "-------------------------finished"
        self.finished_callback()
        
    def terminated(self):
        print "--------------------terminated"
        self.terminated_callback()


g_upload_mgr = None
def GetUploadMgr():
    global g_upload_mgr
    if g_upload_mgr is None:
        g_upload_mgr = UploadMgr()
    return g_upload_mgr

