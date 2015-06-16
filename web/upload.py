# -*- coding:utf-8 -*-
'''
    file: upload.py
    date: 2011-10-15
    desc: 上传画像接口

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

import web
import os
import sys
import random

web.config.debug = False
sys.stdout = sys.stderr

abspath = os.path.dirname("/home/alan/dsf_trunk/bin/unix32/draw/web/")
#abspath = os.path.dirname("/data/draw/web/")
sys.path.append(abspath)
os.chdir(abspath)

from web_token import WebToken
from web_common import WebCommon
from datetime import date
import hashlib

from web_dao import *

urls = (
  "", "reupload",
  "/(.*)", "upload"
)

class reupload(object):
    def GET(self): raise web.seeother('/')

class upload(object):
    web_token = WebToken()
    
    def __init__(self):
        self._key_value_dict = {}
        self._filedir = ""
        self._filename = ""
    
    def ParseParams(self, path):
        for key_value_pair in path.split('&'):
            key_value = key_value_pair.split('=')
            if len(key_value) == 2:
                self._key_value_dict[key_value[0]] = key_value[1]
            else:
                return False
                
        return True
    
    def CheckNecessaryParams(self):
        if self._key_value_dict.has_key('keyword') and self._key_value_dict.has_key('name') and self._key_value_dict.has_key('uid') and self._key_value_dict.has_key('chn') and self._key_value_dict.has_key('topchn') and self._key_value_dict.has_key('webtoken'):
            return True
        return False
    
    def CheckIncomingWebToken(self):
        #uid,channel_id,topchannel,name
        token_encode = upload.web_token.upload_encode(self._key_value_dict['uid'],self._key_value_dict['chn'],self._key_value_dict['topchn'])
        print token_encode
        print self._key_value_dict['webtoken']
        if token_encode != self._key_value_dict['webtoken']:
            return False

        return True

    #def GET(self, path):
    #    web.header("Content-Type","text/html; charset=utf-8")
    #    return "<html><head></head><body><form method='POST' enctype='multipart/form-data' action=''><input type='file' name='uploadpicture' /><br/><input type='submit' /></form></body></html>"

    def GenAbsLocation(self):       
        date_flag =  date.today().toordinal() % 100
        chn_flag = int(self._key_value_dict['topchn']) % 100
        
        filedir = "%s%d/" % (WebCommon.UPLOAD_IMAGES_RELATE_LOCATION_FLAG, date_flag)
        if not os.path.exists(WebCommon.UPLOAD_IMAGES_ABS_LOCATION_BASE + filedir):
            os.mkdir(WebCommon.UPLOAD_IMAGES_ABS_LOCATION_BASE + filedir)
        filedir = "%s%d/%d/" % ( WebCommon.UPLOAD_IMAGES_RELATE_LOCATION_FLAG, date_flag, chn_flag)
        if not os.path.exists(WebCommon.UPLOAD_IMAGES_ABS_LOCATION_BASE + filedir):
            os.mkdir(WebCommon.UPLOAD_IMAGES_ABS_LOCATION_BASE + filedir)

        filename = upload.web_token.upload_image_name_encode(date_flag, self._key_value_dict['uid'], chn_flag, random.randint(1,1000)).encode("ascii")
        filename = "%d%s.png" % (random.randint(1,900000)+99999, filename )
        
        self._filedir = filedir
        self._filename = filename

        return (filedir + filename)
        
    def SavePictureToDisk(self):
        if 'uploadpicture' in self._key_value_dict:
            fout = open(self.GenAbsLocation(),'w')
            fout.write(self._key_value_dict.uploadpicture.file.read())
            fout.close()
            return True
        return False
    
    def SavePictureToDB(self):
        web_dao = WebDao()
        web_dao.Open('127.0.0.1', WebDBCommon.WEB_DB_PORT, WebDBCommon.WEB_APP_DB, WebDBCommon.WEB_DB_USER, WebDBCommon.WEB_DB_PASSWORD)
    
        return web_dao.SaveImageLocation(int(self._key_value_dict['uid']),self._key_value_dict['name'],self._key_value_dict['keyword'], int(self._key_value_dict['chn']), int(self._key_value_dict['topchn']),self._filedir,self._filename,int(self._key_value_dict['shortchn']))
    
    def SavePicture(self):
        if self.SavePictureToDisk():
            return self.SavePictureToDB()
        return False
    
    def POST(self, path):
        self._key_value_dict = web.input(uploadpicture={})
        
        if not self.CheckNecessaryParams():
            return "Invalid params"
            
        #if not self.CheckIncomingWebToken():
        #    return "Invalid params"
        
        self.SavePicture()

        return "OK"
        
        #raise web.seeother('/upload')
        
        #for key in self._key_value_dict:
        #    print key, type(self._key_value_dict[key])

app_upload = web.application(urls, locals())
