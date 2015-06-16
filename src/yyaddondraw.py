# -*- coding:utf-8 -*-
'''
    author: lSaint
    date: 2011-09-29
    desc: 入口

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''


import sip, sys
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from main_window import GuessWindow
from launcher import Launcher

from game import GameMgr


class Machine(QObject):

    def __init__(self, main_window, launcher_window):
        self.state_machine = QStateMachine()
        self.launcher_window = launcher_window
        self.main_window = main_window

        self.game = GameMgr(launcher_window, main_window)
        self.game.InitUI()

        self.launcher_state = QState(self.state_machine)
        self.main_state = QState(self.state_machine)
        self.state_machine.setInitialState(self.launcher_state)

        self.launcher_state.assignProperty(self.launcher_window, "visible", True)
        self.launcher_state.assignProperty(self.main_window, "visible", False)

        self.main_state.assignProperty(self.launcher_window, "visible", False)
        self.main_state.assignProperty(self.main_window, "visible", True)

        self.launcher_state.addTransition(self.launcher_window.button_enter_root.clicked, self.main_state)
        self.launcher_state.addTransition(self.launcher_window.button_enter_child.clicked, self.main_state)
        self.main_state.addTransition(self.main_window.button_back.clicked, self.launcher_state)

        self.state_machine.start()



if __name__ == '__main__':
    app=QApplication(sys.argv)
    machine = Machine(GuessWindow(), Launcher())
    sys.exit(app.exec_())

