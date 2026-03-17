"""
Done using no pre-made modules for qr code creation such as qrcode, pyqrcode, or other.
Any and all classes for qr code creation were coded by myself, not copied from the internet.
This was made as a proof of skill and knowledge.

Began on March 10th 2026
"""

import os
import random
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QLineEdit,
    QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

class Program:
    def __init__(self):
        '''Wrapper class for the window and application objects, containing the actual code of the script.'''
        self.app = Application()
        self.window = Window()
    def execute(self):
        '''Executes the program.'''
        self.window.show()
        self.app.exec()
        print('test')

class Application(QApplication):
    def __init__(self):
        super().__init__([])

class Window(QWidget):
    def __init__(self):
        '''Initializes the UI for the application.'''
        super().__init__()
        self._setupWindow()
        self._setBackgroundColor((34, 19, 41))
        self._createTopBar()

    def usableHeight(self):
        '''Returns the height of the window excluding the top bar, AKA the "usable" height.'''
        return self.height()-self.topBar.height()

    def test(self, event):
        print('Top Bar was clicked!')
    
    def _setupWindow(self):
        '''Creates and sets up the window geometry'''
        SCREENW,SCREENH,HEIGHT,WIDTH,X,Y = self._calculateWindowGeometry()
        # The value fullHeight represents the height of the window, including the top bar created by _createTopBar().
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(X,Y,WIDTH,HEIGHT)

    def _setBackgroundColor(self, backgroundColor):
        '''Sets the color of the main window's background to the specified RGB color.'''
        palette = self.palette()
        color = QColor(*backgroundColor)
        palette.setColor(QPalette.ColorRole.Window, color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def _createTopBar(self):
        '''Creates the custom bar at the top of the window, with the buttons to control said window.'''
        self.topBar = TopBar(self)
        self.topBar.setFixedSize(self.width(), 50)
        self.topBar.move(0,0)
        self.topBar.setStyleSheet("background-color: #160c1e;")
        # The value usableHeight represents the height of the window,
        # excluding the top bar created here, AKA the "usable" height.
        
        
    def _calculateWindowGeometry(self):
        '''Creates some constants used for UI creation'''
        availableSpace = self.screen().availableGeometry()
        SCREENW = availableSpace.width()
        SCREENH = availableSpace.height()
        HEIGHT = int(SCREENH*0.9)
        WIDTH = int(SCREENW*0.7)
        X = SCREENW//2-WIDTH//2
        Y = SCREENH//2-HEIGHT//2
        return SCREENW,SCREENH,HEIGHT,WIDTH,X,Y

class TopBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        

if __name__ == '__main__':
    program = Program()
    program.execute()



















