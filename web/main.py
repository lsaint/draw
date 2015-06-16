# -*- coding:utf-8 -*-
'''
    file: main.py
    date: 2011-10-15
    desc: web主接口

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

import upload
from web_token import WebToken
from web_common import WebCommon
from web_dao import *

from mako.template import Template
from mako.lookup import TemplateLookup

urls = (
  "/upload", upload.app_upload,
  "/(.*)", "index"
)

class index(object):
    web_token = WebToken()
    def __init__(self):
        self._key_value_dict = {}
    
    def ParseParams(self, path):
        self._key_value_dict = {}
        for key_value_pair in path.split('&'):
            key_value = key_value_pair.split('=')
            if len(key_value) == 2:
                self._key_value_dict[key_value[0]] = key_value[1]
            else:
                return False
                
        return True
    
    def CheckNecessaryParams(self):
        if self._key_value_dict.has_key('topchn') and self._key_value_dict.has_key('webtoken') and self._key_value_dict['topchn'] > 0:
            return True
        return False
    
    def CheckIncomingWebToken(self):        
        token_encode = index.web_token.index_encode(self._key_value_dict['topchn'])
        print "coming topchannel" + self._key_value_dict['topchn']
        print token_encode
        print self._key_value_dict['webtoken']
        if token_encode != self._key_value_dict['webtoken']:
            return False
            
        return True
    
    def GET(self, path):   
        if not self.ParseParams(path):
            return ""

        if not self.CheckNecessaryParams():
            return ""
            
        if not self.CheckIncomingWebToken():
            return ""
        
        web_dao = WebDao()
        web_dao.Open('127.0.0.1', WebDBCommon.WEB_DB_PORT, WebDBCommon.WEB_APP_DB, WebDBCommon.WEB_DB_USER, WebDBCommon.WEB_DB_PASSWORD)

        topchn_id = int(self._key_value_dict['topchn'])
        
        channel_images_location = web_dao.LoadImageLocation(self._key_value_dict['topchn'])
        full_images_location = web_dao.LoadImageLocation(0)
        good_images_location = web_dao.LoadImageLocation(-1)
        
        if len(channel_images_location) == 0:
            channel_images_location.append([topchn_id,WebCommon.DEFAULT_PICTURE_RELATE_LOCATION,"YY","YY"])
        if len(full_images_location) == 0:
            full_images_location.append([topchn_id,WebCommon.DEFAULT_PICTURE_RELATE_LOCATION,"YY","YY"])
        if len(good_images_location) == 0:
            good_images_location.append([topchn_id,WebCommon.DEFAULT_PICTURE_RELATE_LOCATION,"YY","YY"])
        
        eff_good_images_location = []
        good_amount = len(good_images_location)
        if good_amount > WebCommon.MAX_PICTURE_PER_LINE:
            while len(eff_good_images_location) < WebCommon.MAX_PICTURE_PER_LINE:
                random_id = random.randint(0,len(good_images_location)-1)
                eff_good_images_location.append(good_images_location.pop(random_id))
        else:
            eff_good_images_location = good_images_location

        #template
        drawlookup = TemplateLookup(directories=['template/'], input_encoding='utf-8', output_encoding='utf-8', encoding_errors='replace')
        drawtemplate = drawlookup.get_template("launcher.html")
        
        #render = render_mako( directories=['templates'], input_encoding='utf-8', output_encoding='utf-8', )
        effchn = int(self._key_value_dict['topchn'])
        if len(channel_images_location) > 0 and len(channel_images_location[0]) >= 5:
            effchn = int(channel_images_location[0][4])

        return drawtemplate.render(topchn=effchn,channel_images_location=channel_images_location,full_images_location=full_images_location,good_images_location=eff_good_images_location)
        

#app = web.application(urls, locals())
#app = web.application(urls, globals()).wsgifunc()
application = web.application(urls, globals()).wsgifunc()

#if __name__ == "__main__":
#    app.run()
      