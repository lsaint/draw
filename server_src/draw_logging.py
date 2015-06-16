# -*- coding:utf-8 -*-
'''
    file: draw_logging.py
    auth: xuzhijian
    date: 2011-07-15
    desc: python日志类封装

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

import logging
import logging.handlers

DRAW_LOG_PATH          = "./log"
SYSTEM_FATAL_ERROR_LOG = "system_fatal_error"
SYSTEM_DEBUG_LOG       = "system_debug"
LOGIC_FATAL_ERROR_LOG  = "logic_fatal_error"
LOGIC_DEBUG_LOG        = "logic_debug"
LOGIC_LOGIN_LOG        = "login"
DRAW_ROUND_LOG         = "draw_round"
DB_LOG                 = "db"
SUGGESTION_LOG         = "suggestion"

def init_draw_logging():
    import os
    if not os.path.exists(DRAW_LOG_PATH):
        os.mkdir(DRAW_LOG_PATH)
        
    all_loggers = [SYSTEM_FATAL_ERROR_LOG,SYSTEM_DEBUG_LOG,LOGIC_FATAL_ERROR_LOG,LOGIC_DEBUG_LOG,LOGIC_LOGIN_LOG,DRAW_ROUND_LOG,DB_LOG,SUGGESTION_LOG]
    
    for _logger_name in all_loggers:
        _logger = logging.getLogger(_logger_name)
        _logger.setLevel(logging.DEBUG)
        
        file_handler = logging.handlers.TimedRotatingFileHandler("%s/%s.log" % (DRAW_LOG_PATH,_logger_name), 'D', 1, 90)
        #file_handler = logging.FileHandler("%s/%s.log" % (DRAW_LOG_PATH,_logger_name))
        file_handler.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        
        formatter = logging.Formatter("[%(levelname)s, %(asctime)s] [%(process)d] %(filename)s:%(lineno)d %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        _logger.addHandler(file_handler)
        _logger.addHandler(console_handler)
        
        _logger.info("init %s ok" % _logger_name)
    