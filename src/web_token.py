# -*- coding:utf-8 -*-
'''
    file: web_token.py
    date: 2011-10-15
    desc: draw web系统通讯验证token类

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

from web_common import *
import datetime
import hashlib

class WebToken(object):
    def index_encode(self,source_str):
        weeknum = datetime.date.today().isocalendar()[1]
        now = datetime.datetime.now()
        minute_flag = ( now.minute + 37 ) / 15
        
        source_str = ("%d%d%s%d%d%d") % (minute_flag,weeknum,source_str,now.day,now.month,now.hour)
        encode_str = hashlib.md5(WebTokenCommon.TOKEN_INDEX_KEY + source_str)
        return unicode(encode_str.hexdigest())
        
    def upload_encode(self,uid,channel_id,topchannel):
        weeknum = datetime.date.today().isocalendar()[1]
        now = datetime.datetime.now()
        minute_flag = ( now.minute + 13 ) / 15
        
        source_str = ("%d%d%d%d%d%d%d") % (uid, minute_flag, channel_id, weeknum,topchannel,now.day,now.month)
        encode_str = hashlib.md5(WebTokenCommon.TOKEN_UPLOAD_KEY + source_str)
        return unicode(encode_str.hexdigest())
        
    def upload_image_name_encode(self, date_flag, uid, chn_flag, param ):
        encode_str = hashlib.md5( "%s%d%s%d%d" % (WebCommon.UPLOAD_IMAGES_NAME_KEY, date_flag, uid, chn_flag, param) )
        return unicode(encode_str.hexdigest())
