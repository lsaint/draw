# -*- coding:utf-8 -*-
'''
    file: mode.py
    auth: xuzhijian
    date: 2011-08-13
    desc: 网络画板游戏模式-游戏模式基类以及派生类
          一个模式下可以有多个不同的状态State派生类，请查看state.py

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''

from state import *

class Mode(object):
    def __init__(self):
        self._cur_state = 0
        self._state_amount = 0
        self._state_contrainer = {}
        
    def ModeStop(self):
        self.GetCurState().StateStop()
        
    def GetCurState(self):
        return self.GetSpecState(self._cur_state)
                
    def SetCurState(self, new_state):
        self._cur_state = new_state
        
    def SetNextState(self,timer_time):
        pass
        
    def GetCurStateId(self):
        return self._cur_state
        
    def SetStateAmount(self,amount):
        self._state_amount = amount
        
    def GetStateAmount(self):
        return self._state_amount
        
    def GetGameModeId(self):
        return self._game_mode_id
        
    def SetGameModeId(self, game_mode_id):
        self._game_mode_id = game_mode_id
        
    def GetSpecState(self, state_id):
        return self._state_contrainer.get(state_id)
        
class AlternationMode(Mode):
    def __init__(self,channel):
        Mode.__init__(self)
        self.SetGameModeId(ALTERNATION_TURN)
        
        self._state_contrainer[ALTERNATION_ESTIMATE_STATE] = AlternationEstimateState(channel)
        self._state_contrainer[ALTERNATION_GAME_STATE] = AlternationGameState(channel)
        self.SetCurState(ALTERNATION_ESTIMATE_STATE)
        self.SetStateAmount(2)
        
    def ModeRefresh(self):
        self.SetCurState(ALTERNATION_ESTIMATE_STATE)
        self.GetCurState().StateStart(0)
        
    def SetNextState(self,timer_time):
        cur_state_id = self.GetCurStateId()
        
        self.GetCurState().StateStop()
        if cur_state_id == ALTERNATION_ESTIMATE_STATE:
            self.SetCurState(ALTERNATION_GAME_STATE)            
        elif cur_state_id == ALTERNATION_GAME_STATE:
            self.SetCurState(ALTERNATION_ESTIMATE_STATE)
        self.GetCurState().StateStart(timer_time)

        
class PresidingMode(Mode):
    def __init__(self,channel):
        Mode.__init__(self)
        self.SetGameModeId(PRESIDING_TURN)
        
        self._state_contrainer[PRESIDING_DRAW_STATE] = PresidingDrawState(channel)
        self.SetCurState(PRESIDING_DRAW_STATE)
        self.SetStateAmount(1)

    def ModeRefresh(self):
        self.SetCurState(PRESIDING_DRAW_STATE)
        self.GetCurState().StateStart(0)
        
class StandradMode(Mode):
    def __init__(self,channel):
        Mode.__init__(self)
        self.SetGameModeId(STANDRAD_TURN)
        
        self._state_contrainer[ESTIMATE_STATE] = EstimateState(channel)
        self._state_contrainer[APPLY_STATE] = ApplyState(channel)
        self._state_contrainer[GAME_STATE] = GameState(channel)
        self.SetCurState(APPLY_STATE)
        self.SetStateAmount(3)
    
    def ModeRefresh(self):
        self.SetCurState(APPLY_STATE)
        self.GetCurState().StateStart(0)
    
    def SetNextState(self,timer_time):
        cur_state_id = self.GetCurStateId()
        
        self.GetCurState().StateStop()
        if cur_state_id == ESTIMATE_STATE:
            self.SetCurState(APPLY_STATE)            
        elif cur_state_id == APPLY_STATE:
            self.SetCurState(GAME_STATE)
        elif cur_state_id == GAME_STATE:
            self.SetCurState(ESTIMATE_STATE)
        self.GetCurState().StateStart(timer_time)

        