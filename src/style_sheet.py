# -*- coding: utf-8 -*-
'''
    file: style_sheet.py
    author: lSaint
    date: 2011-07-20
    desc: 你画我猜 Qt样式表

    广州华多网络科技有限公司 版权所有 (c) 2005-2011 DuoWan.com [多玩游戏]
'''


sh_scroll_h = ''' 
QScrollBar:horizontal {
        background: #DCC7A9;
        height: 6px;
        margin: 0px 20px 0 20px;
        }
QScrollBar::handle:horizontal {
        background: #978676;
        min-width: 5px;
        }
QScrollBar::add-line:horizontal {
        background: #d2c6b8;
        width: 20px;
        subcontrol-position: right;
        subcontrol-origin: margin;
        }
QScrollBar::sub-line:horizontal {
        background: #d2c6b8;
        width: 20px;
        subcontrol-position: left;
        subcontrol-origin: margin;
        }
QScrollBar:left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
        width: 3px;
        height: 3px;
        background: #978676;
        }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
        background: none;
        }
'''

sh_scroll_v = '''
QScrollBar:vertical {
        background: transparent;
        width: 6px;
        margin: 2px 0 2px 0;
        }
QScrollBar::handle:vertical {
        background: #6E6E6E;
        min-height: 10px;
        }
QScrollBar::add-line:vertical {
        background: transparent;
        height: 0px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
        }
QScrollBar::sub-line:vertical {
        background: transparent;
        height: 0px;
        subcontrol-position: top;
        subcontrol-origin: margin;
        }
QScrollBar:up-arrow:vertical, QScrollBar::down-arrow:vertical {
        width: 3px;
        height: 0px;
        background: transparent;
        }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
        }
'''

sh_button_blue = '''
QToolButton {
    border-image: url(:/image/blue.png);
    background-color: transparent;
}
QToolButton:pressed {
    border-image: url(:/image/blue_press.png); 
    background-color: transparent;
}
'''
sh_button_red = '''
QToolButton {
    border-image: url(:/image/red.png);
    background-color: transparent;
}
QToolButton:pressed {
    border-image: url(:/image/red_press.png); 
    background-color: transparent;
}
'''
sh_button_yellow = '''
QToolButton {
    border-image: url(:/image/yellow.png);
    background-color: transparent;
}
QToolButton:pressed {
    border-image: url(:/image/yellow_press.png); 
    background-color: transparent;
}
'''
sh_button_green = '''
QToolButton {
    border-image: url(:/image/green.png);
    background-color: transparent;
}
QToolButton:pressed {
    border-image: url(:/image/green_press.png); 
    background-color: transparent;
}
'''
sh_button_black = '''
QToolButton {
    border-image: url(:/image/black.png);
    background-color: transparent;
}
QToolButton:pressed {
    border-image: url(:/image/black_press.png); 
    background-color: transparent;
}
'''

href_style = '''
a {
text-decoration: none;
color: #7DA231;
}
'''
