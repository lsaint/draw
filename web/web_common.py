# -*- coding:utf-8 -*-
'''
    file: web_common.py
    date: 2011-10-15
    desc: draw web系统基础设定类

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

class WebTokenCommon(object):
    TOKEN_INDEX_KEY  = "38AdkzlkQ78DbZdks8244fkzAqUmnv89Bxxf12"
    TOKEN_UPLOAD_KEY = "289ZdklzoIu378Bxkzlapoqc13cxajUskSSgoi"
    
class WebDBCommon(object):
    WEB_APP_DB_TABLE = "web_upload_images"
    WEB_APP_DB = "web_app_db"
    WEB_DB_PASSWORD = "218"
    WEB_DB_USER = "root"
    WEB_DB_PORT = 3306
        
class WebCommon(object):
    UPLOAD_IMAGES_ABS_LOCATION_BASE = "/home/alan/dsf_trunk/bin/unix32/draw/web/"
    UPLOAD_IMAGES_RELATE_LOCATION_FLAG = "static/upload/images/"
    #UPLOAD_IMAGES_ABS_URL_BASE = "http://172.16.42.30/draw/upload/"
    UPLOAD_IMAGES_ABS_URL_BASE = "http://117.25.132.156/draw/upload/"
    UPLOAD_IMAGES_NAME_KEY = "di32AjcoP18346Adklz99czJKs38910FFds89"
    #INFO_WEB_URL = "http://172.16.42.30/draw/static/info.html"
    INFO_WEB_URL = "http://117.25.132.156/draw/static/info.html"
    #PICTURE_WEB_URL = "http://172.16.42.30/draw/"
    PICTURE_WEB_URL = "http://117.25.132.156/draw/"
    DEFAULT_PICTURE_RELATE_LOCATION = "static/images/nopic.png"
    MAX_PICTURE_PER_LINE = 3