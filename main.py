"""
Done using no pre-made modules for qr code creation such as qrcode, pyqrcode, or other.
Any and all classes for qr code creation were coded by myself, only few snippets may have come from
the internet, which were then adapted for this code specifically.

This was made as a proof of skill and knowledge in both simple app making (with GUI), tinkering
with data (creating the QR CODE itself), and general Python knowledge.

Began on March 10th 2026.
"""

import os
import random
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QLineEdit,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtGui import (
    QPalette,
    QColor,
    QPainter,
    QImage,
)
from PyQt6.QtCore import Qt

class Program:
    '''Wrapper class for the window and application instances.'''
    def __init__(self):
        self.app = Application()
        self.window = Window()
    def execute(self):
        '''Executes the program.'''
        self.window.show()
        self.app.exec()

class Application(QApplication):
    def __init__(self):
        super().__init__([])

class Window(QWidget):
    def __init__(self):
        '''Initializes the UI for the application.'''
        super().__init__()
        self._setupWindowGeometry()
        self._setBackgroundColor((34, 19, 41))
        self._initLayout()
        self.topBar = TopBar(self)
        self._createWorkingAreaWidgets()
        self._placeAllWidgets()
    
    def _setupWindowGeometry(self):
        '''Creates and sets up the window geometry.'''
        SCREENW,SCREENH,HEIGHT,WIDTH,X,Y = self._calculateWindowGeometry()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(X,Y,WIDTH,HEIGHT)

    def _setBackgroundColor(self, backgroundColor):
        '''Sets the color of the main window's background to the specified RGB color.'''
        palette = self.palette()
        color = QColor(*backgroundColor)
        palette.setColor(QPalette.ColorRole.Window, color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def _initLayout(self):
        '''Initializes all the layouts that will automatically arrange all the widgets in the window.'''
        self.outerLayout = QVBoxLayout()
        self.outerLayout.setContentsMargins(0, 0, 0, 0)
        self.outerLayout.setSpacing(0)
        
        self.workingAreaLayout = QHBoxLayout()
        self.workingAreaLayout.setContentsMargins(0, 0, 0, 0)
        self.workingAreaLayout.setSpacing(0)
        
        self.userInputLayout = QVBoxLayout()
        self.userInputLayout.setContentsMargins(0, 0, 0, 0)
        self.userInputLayout.setSpacing(0)

    def _createWorkingAreaWidgets(self):
        '''Creates the widgets that will make up the middle of the window, excluding the top bar, AKA the "Working Area".'''
        self.titleLabel = QLabel(self)
        self.titleLabel.setText("QR CODE GENERATOR")

        
        
        self.QRCodeArea = QRWidget(self)
        

    def _placeAllWidgets(self):
        '''Places all the widgets into their respective layouts/positions.'''
        self.outerLayout.addWidget(self.topBar)
        self.setLayout(self.outerLayout)
        
    def _calculateWindowGeometry(self):
        '''Creates some constants used for UI creation.'''
        availableSpace = self.screen().availableGeometry()
        SCREENW = availableSpace.width()
        SCREENH = availableSpace.height()
        HEIGHT = int(SCREENH*0.9)
        WIDTH = int(SCREENW*0.7)
        X = SCREENW//2-WIDTH//2
        Y = SCREENH//2-HEIGHT//2
        return SCREENW,SCREENH,HEIGHT,WIDTH,X,Y

class QRWidget(QWidget):
    def __init__(self, parent):
        '''Initializes the widget that displays the QR Code.'''
        super().__init__(parent)
   
class TopBar(QWidget):
    def __init__(self, parent):
        '''Initializes the top bar widget.'''
        super().__init__(parent)
        self.setStyleSheet("background-color: #160c1e;")
        self.setFixedHeight(50)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.clickPos = None

    def mousePressEvent(self, event):
        '''Triggered when the widget is clicked by the mouse.'''
        if event.button() == Qt.MouseButton.LeftButton:
            self.onClick(event)
            print('miau')

    def mouseReleaseEvent(self, event):
        '''Triggered when the widget is released from the mouse.'''
        if event.button() == Qt.MouseButton.LeftButton:
            self.onRelease(event)

    def onClick(self, event):
        self.clickPos = event.globalPosition()

    def onRelease(self, event):
        self.clickPos = None

if __name__ == '__main__':
    program = Program()
    program.execute()



















