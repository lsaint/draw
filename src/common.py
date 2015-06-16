# -*- coding:utf-8 -*-
'''
    file: common.py
    author: lSaint
    date: 2011-06-24
    desc: 你画我Y 常量定义

    广州华多网络科技有限公司 版权所有 (c) 2005-2010 DuoWan.com [多玩游戏]
'''

from PyQt4 import QtGui,QtCore
from draw_pb2 import *
import draw_pb2 

g_title = u"你画我歪"

MAIN_VERSION = 0
MINOR_VERSION = 22

# 小于该y坐标时才能拖动窗口
MAX_DRAG_Y_COORDINATE = 35

PEN_SMALL   = 3
PEN_NORMAL  = 9
PEN_BIG     = 18

YELLOW  = QtGui.QColor(255, 207, 0)
RED     = QtGui.QColor(255, 0, 0) 
BLACK   = QtGui.QColor(0, 0, 0)          
GREEN   = QtGui.QColor(0, 172, 37) 
BLUE    = QtGui.QColor(0, 159, 237)
WHITE   = QtGui.QColor(255,255,255)

SCORE_WINDOW_POS = QtCore.QPoint(150, 170)
HELP_WINDOW_POS = QtCore.QPoint(100, 100)

ROOM_COLOE = {INDIVIDUAL_CHANNEL_ROOM:"blue",  UNIVERSAL_TOP_CHANNEL_HALL:"green"}

NAME_ROLE = {    
        draw_pb2.PLAYER_ROLE    : u"画手",
        draw_pb2.WATCHER_ROLE   : u"围观者",
        draw_pb2.DRAWING_ROLE   : u"主笔",
    }

CHAT_COLOR_ANNOUNCE = u"<b><font color=#FF0000>%s</b>"
CHAT_COLOR_SYSTEM   = u"<b><font color=#936903>%s</b>"

CHAT_COLOR_OBSERVER = u"<font color=#6ACEEE>"
CHAT_STYLE_OBSERVER = CHAT_COLOR_OBSERVER + u"发送给围观者"

CHAT_COLOR_PLAYER   = u"<font color=#0754AC>"
CHAT_STYLE_PLAYER   = CHAT_COLOR_PLAYER + u"发送给绘画者"

CHAT_COLOR_PRIVATE  = u"<font color=#FF76ED>"
CHAT_STYLE_PRIVATE_PRE = CHAT_COLOR_PRIVATE + u"发送给"
CHAT_STYLE_PRIVATE_SUF = CHAT_COLOR_PRIVATE + u"对你说"

TIP_NO_AUTHORITY = u"你没有权限"
TIP_RE_SETTING = u"重复设置"


HOST_BACKGROUND_COLOR = QtGui.QColor(81,50,22,100)
OFFLINE_BACKGROUND_COLOR = QtGui.QColor(31, 25, 11, 50)


UI_GAME_MODE = {
        draw_pb2.ALTERNATION_TURN   : 0, 
        draw_pb2.PRESIDING_TURN     : 1, 
        draw_pb2.STANDRAD_TURN      : 2, 
        }
NAME_GAME_MODE = {
        draw_pb2.ALTERNATION_TURN   : u"轮流模式",
        draw_pb2.PRESIDING_TURN     : u"主持模式",
        draw_pb2.STANDRAD_TURN      : u"标准模式", 
        }
UI_GAME_MODE_R = dict((v,k) for k,v in UI_GAME_MODE.items())


UI_TALK_MODE = {
                draw_pb2.CHAT_CONFIG_RELEASE_ALL:0,
                draw_pb2.CHAT_CONFIG_BAN_WATCHER_ONLY:1, 
                draw_pb2.CHAT_CONFIG_BAN_ALL:2,
               }
UI_TALK_MODE_R = dict((v,k) for k,v in UI_TALK_MODE.items())
NAME_TALK_MODE = {
                draw_pb2.CHAT_CONFIG_BAN_ALL:u"禁言所有人",
                draw_pb2.CHAT_CONFIG_BAN_WATCHER_ONLY:u"禁言围观者", 
                draw_pb2.CHAT_CONFIG_RELEASE_ALL:u"自由发言",
               }

UI_CHL_WORD_RATE = {
                draw_pb2.CHANNEL_DICTIONARY_RATE_NONE   : 0,
                draw_pb2.CHANNEL_DICTIONARY_RATE_LOW    : 1, 
                draw_pb2.CHANNEL_DICTIONARY_RATE_MIDDLE : 2,
                draw_pb2.CHANNEL_DICTIONARY_RATE_HIGH   : 3,
               }
UI_CHL_WORD_RATE_R = dict((v,k) for k,v in UI_CHL_WORD_RATE.items())
NAME_CHL_WORD_RATE = {
                draw_pb2.CHANNEL_DICTIONARY_RATE_NONE   : u"不使用",
                draw_pb2.CHANNEL_DICTIONARY_RATE_LOW    : u"低比例", 
                draw_pb2.CHANNEL_DICTIONARY_RATE_MIDDLE : u"中比例",
                draw_pb2.CHANNEL_DICTIONARY_RATE_HIGH   : u"高比例",
               }


# 权限分界点
AUTHORITY_BONUD = draw_pb2.APP_YYCHANNEL_CMANAGER_ROLE

PING_INTERVAL = 60 * 1000
SEND_INTERVAL = 300
COUNT_INTERVAL = 1000
TIP_INTERVAL = 4000
UPLOAD_INTERVAL = 60000

MAX_CHAT_NAME_LEN = 20
MAX_CHAT_TARGET_COUNT = 7 # 包括分隔符
RECENT_TALK_BEGIN_INDEX = 4

POP_MENU_SET_HOST = 1
POP_MENU_TALK_TO = 2
POP_MENU_SET_OB = 3
POP_MENU_GET_DETAIL = 4

MAX_DICE_COUNT = 3

# QTableListWidget
COL_NAME = 0
COL_DICE = 1

LEN_COL_NAME = 220
LEN_COL_DICE = 38
#

# special action
SP_ACTION_ROLL = u"/roll"
#


ITME_NAME = {OBJ_CATEGORY_FLOWER:u"鲜花", OBJ_CATEGORY_EGG:u"鸡蛋"}
GAIN_ITEM_TIP = {OBJ_CATEGORY_FLOWER:u"你的可使用道具(鲜花)增加了一朵",\
        OBJ_CATEGORY_EGG:u"你的可使用道具(鸡蛋)增加了一个"}

FLOWER_COLOR_NAME = u"<font color='red'>鲜花</font>"
EGG_COLOR_NAME = u"<font color='#FFAA00'>鸡蛋</font>"


MAX_LAUNCHER_ROOM_NAME = 36

def ENCODEGB1(string):
    return string.encode("gb18030")

def DECODEGB1(string):
    return string.decode("gb18030")


DRAW_SERVICE_ID = 101

DRAW_PROTOCOL_ID_DICT = {
         "dc2ds_login_request"                   :   1,
         "ds2dc_login_response"                  :   2,
         "ds2dc_change_subchannel"               :   3,
         "ds2dc_add_drawer_list"                 :   4,
         "ds2dc_remove_drawer_list"              :   5,
         "ds2dc_set_master_drawer"              :   6,
         "dc2ds_master_draw_action"             :   7,
         "ds2dc_draw_action"                    :   8,
         "dc2ds_logout_request"                 :   9,
         "dc2ds_set_master_type_request"        :   10,
         "ds2dc_set_master_type_response"       :   11,
         "ds2dc_set_master_type_notification"   :   12,
         "dc2ds_change_role_request"            :   13,
         "ds2dc_change_role_response"           :   14,
         "ds2dc_change_role_notification"       :   15,
         "ds2dc_change_yyrole_notification"     :   16,
         "dc2ds_chat_request"                  :   17,
         "ds2dc_chat_response"                 :   18,
         "ds2dc_chat_notification"             :   19,
         "dc2ds_config_request"                :   20,
         "ds2dc_config_response"               :   21,
         "ds2dc_config_notification"           :   22,
         "dc2ds_chat_config_request"           :   23,
         "ds2dc_chat_config_response"          :   24,
         "ds2dc_chat_config_notification"      :   25,
         "dc2ds_ping"                            : 26,
         "ds2dc_quit_notification"               : 27,
         "ds2dc_estimate_state"                  : 28,
         "ds2dc_apply_state"                     : 29,
         "dc2ds_apply_drawer_request"            : 30,
         "ds2dc_apply_drawer_response"           : 31,
         "ds2dc_apply_drawer_notification"       : 32,
         "ds2dc_game_state"                      : 33,
         "ds2dc_first_hit_keyword_notification"  : 34,
         "dc2ds_manage_channel_words_request" : 35,
         "ds2dc_manage_channel_words_response": 36,
         "dc2ds_update_channel_words_request" : 37,
         "ds2dc_update_channel_words_response": 38,
         "dc2ds_submit_words_request"         : 39,
         "dc2ds_make_suggestions"             : 40,
         "dc2ds_login_launcher_request"          :41,
         "dc2ds_login_launcher_response"         :42,
         "ds2dc_gain_item_notification"          :43,
         "dc2ds_use_item_request"                :44,
         "ds2dc_use_item_response"               :45,
         "ds2dc_use_item_notification"           :46,
         "dc2ds_get_score_request"               :47,
         "ds2dc_get_score_response"              :48,
         "dc2ds_start_action_request"         :49,
         "ds2dc_start_action_response"        :50,
         "ds2dc_start_action_notification"    :51,
         "dc2ds_stop_action_request"          :52,
         "ds2dc_stop_action_response"         :53,
         "ds2dc_stop_action_notification"     :54,
         "ds2dc_chn_action_score_notification":55,
}



