"""
Done using no pre-made modules for qr code creation such as qrcode, pyqrcode, or other.
Any and all classes for qr code creation were coded by myself, only few snippets may have come from
the internet, which were then adapted for this code specifically.

This was made as a proof of skill and knowledge in both simple app making (with GUI), tinkering
with data (creating the QR CODE itself), and general Python knowledge.

Began on March 10th 2026.
"""
import os
import sys
import ctypes
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QPlainTextEdit,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt6.QtGui import (
    QPalette,
    QColor,
    QPainter,
    QImage,
    QIcon,
    QPixmap,
)
from PyQt6.QtCore import Qt, QSize

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class Program:
    '''Wrapper class for the window and application instances.'''
    def __init__(self):
        self.app = Application()
        self.window = Window()
    def execute(self) -> None:
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
        self.titleBar = TitleBar(self)
        self._createWorkingAreaWidgets()
        self._placeAllWidgets()
        self._stylizeWidgets()
    
    def showEvent(self, event):
        super().showEvent(event)
        if sys.platform == "win32":
            hwnd = int(self.winId())
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            DWMWCP_ROUND = 2
            
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_WINDOW_CORNER_PREFERENCE,
                ctypes.byref(ctypes.c_int(DWMWCP_ROUND)),
                ctypes.sizeof(ctypes.c_int)
            )
    
    def _setupWindowGeometry(self) -> None:
        '''Creates and sets up the window geometry.'''
        HEIGHT,WIDTH,X,Y = self._calculateWindowGeometry()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        #self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(X,Y,WIDTH,HEIGHT)

    def _setBackgroundColor(self, backgroundColor: tuple[int, int, int]) -> None:
        '''Sets the color of the main window's background to the specified RGB color.'''
        palette = self.palette()
        color = QColor(*backgroundColor)
        palette.setColor(QPalette.ColorRole.Window, color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def _initLayout(self) -> None:
        '''Initializes all the layouts that will automatically arrange all the widgets in the window.'''
        self.outerLayout = QVBoxLayout()
        self.outerLayout.setContentsMargins(0, 0, 0, 0)
        self.outerLayout.setSpacing(0)

        self.titleBarLayout = QHBoxLayout()
        self.titleBarLayout.setContentsMargins(0, 0, 0, 0)
        self.titleBarLayout.setSpacing(0)
        
        self.workingAreaLayout = QHBoxLayout()
        self.workingAreaLayout.setContentsMargins(0, 0, 0, 0)
        self.workingAreaLayout.setSpacing(0)
        
        self.userInputLayout = QVBoxLayout()
        self.userInputLayout.setContentsMargins(0, 0, 0, 0)
        self.userInputLayout.setSpacing(0)

        self.qrCodeLayout = QVBoxLayout()
        self.qrCodeLayout.setContentsMargins(0, 0, 0, 0)
        self.qrCodeLayout.setSpacing(0)

        self.qrCodeButtonsLayout = QHBoxLayout()
        self.qrCodeButtonsLayout.setContentsMargins(0, 0, 0, 0)
        self.qrCodeButtonsLayout.setSpacing(0)

        self.setLayout(self.outerLayout)

    def _createWorkingAreaWidgets(self) -> None:
        '''Creates the widgets that will make up the middle of the window, excluding the top bar, AKA the "Working Area".'''
        icon_path = os.path.join(SCRIPT_DIR, "icon.ico")
        self.appIcon = QLabel()
        self.appIcon.setPixmap(QPixmap(icon_path))
        self.appTitle = QLabel("QR Code Generator - Waiting")
        self.appMinButton = QPushButton()
        self.appWinButton = QPushButton()
        self.appCloseButton = QPushButton()
        self.appCloseButton.clicked.connect(self.close)

        self.workingAreaTitle = QLabel("QR CODE GENERATOR")

        self.textEntryTitle = QLabel("Text :")

        self.textEntry = QPlainTextEdit()
        self.textEntry.setPlaceholderText("Text to encode goes here...")
        self.textEntry.setReadOnly(False)

        self.eccButtonGroupTitle = QLabel("Error Correction Level :")
        
        self.lowButton = QRadioButton("Level L (Low) : Up to 7% data recovery.")
        self.mediumButton = QRadioButton("Level M (Medium) : Up to 15% data recovery.")
        self.quartileButton = QRadioButton("Level Q (Quartile) : Up to 25% data recovery.")
        self.highButton = QRadioButton("Level H (High) : Up to 30% data recovery.")

        self.eccButtonGroup = QButtonGroup()
        self.eccButtonGroup.addButton(self.lowButton, 1)
        self.eccButtonGroup.addButton(self.mediumButton, 2)
        self.eccButtonGroup.addButton(self.quartileButton, 3)
        self.eccButtonGroup.addButton(self.highButton, 4)
        self.mediumButton.setChecked(True)

        self.qrCode = QRWidget()
        self.qrCode.setMinimumHeight(self.height()-100)
        self.qrCode.setMinimumWidth(self.height()-100)
        
        self.generateButton = QPushButton("Generate")
        self.generateButton.setAutoDefault(False)

        self.clipboardButton = QPushButton()
        self.clipboardButton.setAutoDefault(False)
        icon_path = os.path.join(SCRIPT_DIR, "copy.ico")
        self.clipboardButton.setIcon(QIcon(icon_path))
        self.clipboardButton.setIconSize(QSize(32, 32))

        self.downloadButton = QPushButton()
        self.downloadButton.setAutoDefault(False)
        icon_path = os.path.join(SCRIPT_DIR, "download.ico")
        self.downloadButton.setIcon(QIcon(icon_path))
        self.downloadButton.setIconSize(QSize(32, 32))

    def _placeAllWidgets(self) -> None:
        '''Places all the widgets into their respective layouts/positions.'''
        self.outerLayout.addWidget(self.titleBar)
        self.outerLayout.addLayout(self.workingAreaLayout)

        self.titleBar.setLayout(self.titleBarLayout)
        self.titleBarLayout.addWidget(self.appIcon)
        self.titleBarLayout.addWidget(self.appTitle)
        self.titleBarLayout.addWidget(self.appMinButton)
        self.titleBarLayout.addWidget(self.appWinButton)
        self.titleBarLayout.addWidget(self.appCloseButton)

        self.workingAreaLayout.addLayout(self.userInputLayout)
        self.workingAreaLayout.addLayout(self.qrCodeLayout)
        
        self.userInputLayout.addWidget(self.workingAreaTitle)
        self.userInputLayout.addWidget(self.textEntryTitle)
        self.userInputLayout.addWidget(self.textEntry)
        self.userInputLayout.addWidget(self.eccButtonGroupTitle)
        self.userInputLayout.addWidget(self.lowButton)
        self.userInputLayout.addWidget(self.mediumButton)
        self.userInputLayout.addWidget(self.quartileButton)
        self.userInputLayout.addWidget(self.highButton)

        self.qrCodeLayout.addWidget(self.qrCode)
        self.qrCodeLayout.addLayout(self.qrCodeButtonsLayout)

        self.qrCodeButtonsLayout.addWidget(self.generateButton)
        self.qrCodeButtonsLayout.addWidget(self.clipboardButton)
        self.qrCodeButtonsLayout.addWidget(self.downloadButton)
    
    def _stylizeWidgets(self) -> None:
        '''Applies all of the style to all the widgets'''
        pass
        
    def _calculateWindowGeometry(self) -> tuple[int,int,int,int]:
        '''Creates some constants used for UI creation.'''
        availableSpace = self.screen().availableGeometry()
        SCREENW = availableSpace.width()
        SCREENH = availableSpace.height()
        HEIGHT = int(SCREENH*0.9)
        WIDTH = int(SCREENW*0.7)
        X = SCREENW//2-WIDTH//2
        Y = SCREENH//2-HEIGHT//2
        return HEIGHT,WIDTH,X,Y

class QRWidget(QWidget):
    def __init__(self):
        '''Initializes the widget that displays the QR Code.'''
        super().__init__()
        self.text = ''
   
class TitleBar(QWidget):
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