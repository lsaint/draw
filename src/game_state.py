# -*- coding:utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *


def AddTransition(lt, sig, target_state):
    for state in lt:
        if state != target_state:
            state.addTransition(sig, target_state)



class RoleState(QState):

    def __init__(self, p, callback):
        super(RoleState, self).__init__(p)
        self.callback = callback


    def onEntry(self, event):
        self.callback()



class DrawingState(RoleState):
    pass


class PlayerState(RoleState):
    pass


class WatcherState(RoleState):
    pass


class AppraiseState(RoleState):
    pass



class RestState(RoleState):
    pass


# === === === === === === === === === === === === ===


class GameModeState(QState):
    
    def __init__(self, machine, window, game):
        super(GameModeState, self).__init__(machine)
        self.window = window
        self.game = game

        self.drawing_state = DrawingState(self, self.OnEntryDrawing) 
        self.player_state = PlayerState(self, self.OnEntryPlayer)
        self.watcher_state = WatcherState(self, self.OnEntryWatcher)
        self.appraise_state = AppraiseState(self, self.OnEntryAppraise)
        self.rest_state = RestState(self, self.OnEntryRest)
        self.role_state_list = [self.drawing_state, self.player_state, self.watcher_state,\
                                self.appraise_state, self.rest_state]
        AddTransition(self.role_state_list, self.machine().sig_drawing_state, self.drawing_state)
        AddTransition(self.role_state_list, self.machine().sig_player_state, self.player_state)
        AddTransition(self.role_state_list, self.machine().sig_watcher_state, self.watcher_state)
        AddTransition(self.role_state_list, self.machine().sig_rest_state, self.rest_state)
        AddTransition(self.role_state_list, self.machine().sig_apprise_state, self.appraise_state)
        self.setInitialState(self.rest_state)


    def onEntry(self, event):
        self.game.standard_mgr.key_word = ""


    def OnEntryDrawing(self):
        print "---OnEntryDrawing"
        self.game.appraise_panel.Hide()
        self.game.host_card.Hide()
        self.window.label_keyword.show()
        #self.window.button_ob.show()
        #self.window.button_draw.hide()


    def OnEntryPlayer(self):
        print "---OnEntryPlayer"
        self.window.label_keyword.hide()
        self.game.appraise_panel.Hide()
        self.game.host_card.Show()
        #self.window.button_ob.show()
        #self.window.button_draw.hide()


    def OnEntryWatcher(self):
        print "---OnEntryWatcher"
        self.window.label_keyword.hide()
        self.game.appraise_panel.Hide()
        self.game.host_card.Show()
        #self.window.button_draw.show()
        #self.window.button_ob.hide()


    def OnEntryAppraise(self):
        print "---OnEntryAppraise"
        self.window.label_keyword.hide()
        self.game.host_card.Hide()
        #self.window.button_draw.show()
        #self.window.button_ob.hide()
        self.game.appraise_panel.Show()


    def OnEntryRest(self):
        print "---OnEntryRest"
        self.window.label_keyword.hide()
        self.game.appraise_panel.Hide()
        self.game.host_card.Hide()
        #self.window.button_draw.show()
        self.window.button_draw.setEnabled(True)
        #self.window.button_ob.hide()



class StandardModeState(GameModeState):

    def onEntry(self,event):
        print "+++StandardModeState"
        self.game.host_card.ShowAsLine()


    def OnEntryWatcher(self):
        print "++ -- standard mode watcher"
        GameModeState.OnEntryWatcher(self)
        self.window.button_draw.setEnabled(False)


    def OnEntryAppraise(self):
        GameModeState.OnEntryAppraise(self)
        self.game.standard_mgr.StandardModeAppraise()



class PresideModeState(GameModeState):

    def onEntry(self,event):
        print "+++PresideModeState"
        GameModeState.onEntry(self, event)
        self.game.host_card.ShowAsList()


    def OnEntryPlayer(self):
        GameModeState.OnEntryPlayer(self)
        #self.window.button_ob.show()
        #self.window.button_draw.hide()
 


class AlternationModeState(GameModeState):

    def onEntry(self,event):
        print "+++AlternationModeState"
        GameModeState.onEntry(self, event)
        self.game.host_card.ShowAsList()


    def OnEntryPlayer(self):
        GameModeState.OnEntryPlayer(self)
        #self.window.button_ob.show()
        #self.window.button_draw.hide()
 


class LoadingState(GameModeState):

    def onEntry(self,event):
        print "+++LoadingState"
        GameModeState.onEntry(self, event)
        self.game.host_card.Hide()
        self.window.button_draw.setEnabled(False)


#  === === === === === === === === === === === === 



class GameMachine(QStateMachine):

    sig_standard_state = pyqtSignal()
    sig_preside_state = pyqtSignal()
    sig_alternation_state = pyqtSignal()
    sig_loading_state = pyqtSignal()

    sig_drawing_state = pyqtSignal()
    sig_player_state  = pyqtSignal()
    sig_watcher_state = pyqtSignal()
    sig_rest_state    = pyqtSignal()
    sig_apprise_state = pyqtSignal()

    def __init__(self, window):
        super(GameMachine,self).__init__()
        self.window = window

        self.standard_state = StandardModeState(self, self.window, self)
        self.preside_state = PresideModeState(self, self.window, self)
        self.alternation_state = AlternationModeState(self, self.window, self)
        self.loading_state  = LoadingState(self, self.window, self)
        self.mode_state_list = [self.standard_state, self.preside_state, self.alternation_state, self.loading_state]

        self.setInitialState(self.loading_state)

        AddTransition(self.mode_state_list, self.sig_loading_state, self.loading_state)
        AddTransition(self.mode_state_list, self.sig_standard_state, self.standard_state)
        AddTransition(self.mode_state_list, self.sig_alternation_state, self.alternation_state)
        AddTransition(self.mode_state_list, self.sig_preside_state, self.preside_state)

        self.start()


    def EnterDrawingState(self):
        self.sig_drawing_state.emit()


    def EnterPlayerState(self):
        self.sig_player_state.emit()


    def EnterWatcherState(self):
        self.sig_watcher_state.emit()


    def EnterRestState(self):
        self.sig_rest_state.emit()


    def EnterAppriseState(self):
        self.sig_apprise_state.emit()


    # ===
    def EnterStandardState(self):
        self.sig_standard_state.emit()


    def EnterPreSideState(self):
        self.sig_preside_state.emit()


    def EnterAlternationState(self):
        self.sig_alternation_state.emit()


    def EnterLoadingState(self):
        self.sig_loading_state.emit()


    def GetCurRoleState(self):
        for i in self.configuration():
            if issubclass(type(i), RoleState):
                return i


    def GetCurModeState(self):
         for i in self.configuration():
            if issubclass(type(i), GameModeState):
                return i


