"""
Done using no pre-made modules for qr code creation such as qrcode, pyqrcode, or other.
Any and all classes were coded by myself, not copied from the internet.
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
        self.app = Application()
        self.window = Window()

class Application(QApplication):
    def __init__(self):
        super().__init__([])

class Window(QWidget):
    def __init__(self):
        '''Initializes the UI for the application.'''
        super().__init__()
        self._setupWindow()
        self._setBackgroundColor()
        
    def _setupWindow(self):
        '''Creates and sets up the window geometry'''
        SCREENW,SCREENH,HEIGHT,WIDTH,X,Y = self._calculateWindowGeometry()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(X,Y,WIDTH,HEIGHT)

    def _setBackgroundColor(self):
        color = QColor(98, 32, 159)
        self.palette().setColor(QPalette.ColorRole.Window,color)
        
        
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


if __name__ == '__main__':
    program = Program()
    program.window.show()
    program.app.exec()



















