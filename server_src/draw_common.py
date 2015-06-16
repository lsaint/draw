# -*- coding:utf-8 -*-
'''
    file: draw_common.py
    auth: xuzhijian
    date: 2011-08-13
    desc: 网络画板常数

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

from draw_pb2 import *

class DrawDBConfig(object):
    DB_CONFIG_HOST = ""
    DB_CONFIG_PORT = ""
    DB_CONFIG_NAME = ""
    DB_CONFIG_USER = ""
    DB_CONFIG_PASSWD = ""
    DB_DRAW_DICTIONARY_TABLE = "app_draw_dictionary"
    DB_CHANNEL_DICTIONARY_TABLE = "app_draw_channel_dictionary"
    DB_CHANNEL_DICTIONARY_HISTORY_TABLE = "app_draw_channel_dictionary_history"
    DB_PENDING_SUMMIT_DICTIONARY_TABLE = "app_pending_summit_draw_dictionary"
    DB_DRAW_USER_SCORE_TABLE = "user_score"

class DrawConfig(object):
    MAXWATCHER = 500
    MAXPLAYER = 8
    ROUND_DURATION = 10000
    ROUND_DURATION_SECOND = 10
    ROUND_INTERVAL = 2000
    ROUND_INTERVAL_SECOND = 2
    ROUND_PRESIDING_DURATION_SECOND = 0    # 0表示无限时间
    CONFIG_MAX_CHAT_INTERVAL = 60
    CONFIG_MIN_CHAT_INTERVAL = 1
    BAN_OP = [CONFIG_BAN_ALL,CONFIG_BAN_WATCHER,CONFIG_BAN_ID]
    RELEASE_OP = [CONFIG_RELEASE_ALL,CONFIG_RELEASE_WATCHER,CONFIG_RELEASE_ID]
    
    MAX_DRAW_ACTIONS_AMOUNT = 300
    
    CLIENT_MAIN_VERSION = 0
    CLIENT_MINOR_VERSION = 22
    
    #客户端60秒ping一次
    MAX_PING_IDLE_TIME = 70000
    
    #10分钟自动存盘一次
    MAX_USER_SAVE_TIME = 600000
    
    MAX_ACTION_DURATION = 180
    
class DrawObjConfig(object):
    BAG_INVENTORY_CAPACITY = 2
    
    OBJ_FLOWER_CAPACITY = 3
    OBJ_EGG_CAPACITY = 3
    
    OBJ_FIRST_HIT_REWARD_RATE_BONUS = 20
    
class DrawStateConfig(object):
    APPLY_MAX_AMOUNT = 20
    GAME_STATE_DURATION = 60000
    GAME_STATE_DURATION_SEC = 60
    ESTIMATE_STATE_DURATION = 7000
    ESTIMATE_STATE_DURATION_SEC = 7
    APPLY_STATE_DURATION = 4000
    APPLY_STATE_DURATION_SEC = 4
    GAME_FIRST_HIT_REMAINING_TIME = 10000
    GAME_FIRST_HIT_REMAINING_SEC = 10
    
    ALTERNATION_ESTIMATE_STATE_DURATION = 2000
    ALTERNATION_ESTIMATE_STATE_DURATION_SEC = 2
    ALTERNATION_GAME_STATE_DURATION = 10000
    ALTERNATION_GAME_STATE_DURATION_SEC = 10
    
    PRESIDING_DRAW_STATE_DURATION = 0
    PRESIDING_DRAW_STATE_DURATION_SEC = 0
    
class DrawDictConfig(object):
    CATEGORY_FRUIT = 1          #水果
    CATEGORY_FURNITURE = 2      #家具
    CATEGORY_ANIMAL = 3         #动物
    CATEGORY_NATURA = 4         #自然景观
    CATEGORY_UNKNOWN = 999      #没分类
    
    MAX_CHANNEL_DICTIONARY_WORDS_AMOUNT = 200
    MAX_DICTIONARY_WORDS_LEN = 24

class DrawEventConfig(object):
    EVENT_CHANNEL = 98222421
    EVENT_MONTH = 11
    EVENT_DAY = 4
    EVENT_YEAR = 2011
    EVENT_BEGIN_HOUR = 18