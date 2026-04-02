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
    QTextEdit,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)
from PyQt6.QtGui import (
    QPalette,
    QColor,
    QPainter,
    QImage,
    QIcon,
    QPixmap,
    QCursor,
)
from PyQt6.QtCore import (
    Qt, 
    QSize,
    QPoint,
    QPointF,
)
from math import floor, ceil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class Program:
    '''Wrapper class for the window and application instances.'''
    def __init__(self):
        self.app = Application()
        icon_path = os.path.join(SCRIPT_DIR, "icon.ico")
        self.app.setWindowIcon(QIcon(icon_path))

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
        self._createTitleBarWidgets()
        self._createWorkingAreaWidgets()
        self._initLayout()
        self._placeAllWidgets()
        self._setBackgroundColor((26, 12, 32))
        self._stylizeWidgets()
    
    def maximize(self, event) -> None:
        '''Triggered when TBMaxButton is pressed, or when the title bar is '''
        if (self.isMaximized()) or (self.windowIsMaximized):
            self.windowIsMaximized = False
            self.showNormal()
            self.setGeometry(self.normalPos.x(), self.normalPos.y(), self.normalWidth, self.normalHeight)
            self.TBMaxButton.setIcon(self.maximizeIcon)
        else:
            self.windowIsMaximized = True
            self.showMaximized()
            self.TBMaxButton.setIcon(self.normalizeIcon)
        self.handleWindowEdges()

    def showEvent(self, event) -> None:
        '''Triggered when the window is shown on the screen'''
        super().showEvent(event)
        self.handleWindowEdges()
    
    def handleWindowEdges(self) -> None:
        '''Communicates with the Windows DWM API to handle the window's borders and corners'''
        if sys.platform == "win32":
            hwnd = int(self.winId())
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            if (self.isMaximized()) or (self.windowIsMaximized):
                DWMWCP_ROUND = 1
            else:
                DWMWCP_ROUND = 2
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_WINDOW_CORNER_PREFERENCE,
                ctypes.byref(ctypes.c_int(DWMWCP_ROUND)),
                ctypes.sizeof(ctypes.c_int)
            )

    def _setupWindowGeometry(self) -> None:
        '''Creates and sets up the window geometry.'''
        self.windowIsMaximized = False
        self.gripSize = 8
        # This variable is used to remember whether the window was maximized or not after it gets minimized, as self.isMaximized() doesn't return the correct
        # value whenever the window is minimized while being maximized.
        self.normalPos, self.normalWidth, self.normalHeight = self._calculateWindowGeometry()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        #self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(self.normalPos.x(), self.normalPos.y(), self.normalWidth, self.normalHeight)

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

        self.qrCodeLayout = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.qrCodeLayout.setLayout(layout)

        self.qrCodeButtonsLayout = QHBoxLayout()
        self.qrCodeButtonsLayout.setContentsMargins(0, 0, 0, 0)
        self.qrCodeButtonsLayout.setSpacing(0)

        self.setLayout(self.outerLayout)

    def _createTitleBarWidgets(self) -> None:
        '''Creates the title bar and the widgets that will make it up'''
        self.titleBar = TitleBar(self)

        self.appIcon = QLabel()

        self.appTitle = QLabel("QR Code Generator - Waiting")

        self.TBMinButton = QPushButton()
        self.TBMinButton.clicked.connect(self.showMinimized)

        self.TBMaxButton = QPushButton()
        self.TBMaxButton.clicked.connect(self.maximize)

        self.TBCloseButton = QPushButton()
        self.TBCloseButton.clicked.connect(self.close)

        self.outerLimiter = QWidget()

    def _createWorkingAreaWidgets(self) -> None:
        '''Creates the widgets that will make up the middle of the window, excluding the top bar, AKA the "Working Area".'''
        self.userInputTitle = QLabel("QR CODE GENERATOR")

        self.textEntryTitle = QLabel("Text :")

        self.textEntry = QTextEdit()
        self.textEntry.setPlaceholderText("Text to encode goes here...")
        self.textEntry.setAcceptRichText(False)
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

        self.workingAreaLimiter = QWidget()

        self.qrCode = QRWidget()
        
        self.generateButton = QPushButton("Generate")
        self.generateButton.setAutoDefault(False)

        self.downloadButton = QPushButton()
        self.downloadButton.setAutoDefault(False)

        self.copyButton = QPushButton()
        self.copyButton.setAutoDefault(False)

    def _placeAllWidgets(self) -> None:
        '''Places all the widgets into their respective layouts/positions.'''
        self.outerLayout.addWidget(self.titleBar)
        self.outerLayout.addWidget(self.outerLimiter)
        self.outerLayout.addLayout(self.workingAreaLayout)

        self.titleBar.setLayout(self.titleBarLayout)
        self.titleBarLayout.addWidget(self.appIcon)
        self.titleBarLayout.addWidget(self.appTitle)
        self.titleBarLayout.addWidget(self.TBMinButton)
        self.titleBarLayout.addWidget(self.TBMaxButton)
        self.titleBarLayout.addWidget(self.TBCloseButton)

        self.workingAreaLayout.addLayout(self.userInputLayout)
        self.workingAreaLayout.addWidget(self.workingAreaLimiter)
        self.workingAreaLayout.addWidget(self.qrCodeLayout)
        
        self.userInputLayout.addStretch()
        self.userInputLayout.addWidget(self.userInputTitle)
        self.userInputLayout.addStretch()
        self.userInputLayout.addWidget(self.textEntryTitle)
        self.userInputLayout.addWidget(self.textEntry)
        self.userInputLayout.addStretch()
        self.userInputLayout.addWidget(self.eccButtonGroupTitle)
        self.userInputLayout.addWidget(self.lowButton)
        self.userInputLayout.addWidget(self.mediumButton)
        self.userInputLayout.addWidget(self.quartileButton)
        self.userInputLayout.addWidget(self.highButton)
        self.userInputLayout.addStretch()

        layout = self.qrCodeLayout.layout()
        layout.addStretch()
        layout.addWidget(self.qrCode)
        layout.addLayout(self.qrCodeButtonsLayout)
        layout.addStretch()

        self.qrCodeButtonsLayout.addWidget(self.generateButton)
        self.qrCodeButtonsLayout.addWidget(self.downloadButton)
        self.qrCodeButtonsLayout.addWidget(self.copyButton)
    
    def _stylizeWidgets(self) -> None:
        '''Applies all of the style to all the widgets'''
        titleBarHeight = self.titleBar.height()

        self.outerLimiter.setFixedHeight(1)
        self.outerLimiter.setObjectName("limiter")

        icon_path = os.path.join(SCRIPT_DIR, "icon.svg")
        self.appIcon.setPixmap(QPixmap(icon_path).scaled(25, 25))
        self.appIcon.setContentsMargins(15,0,15,0)
        self.appIcon.setFixedWidth(60)

        icon_path = os.path.join(SCRIPT_DIR, "minimize.svg")
        self.TBMinButton.setIcon(QIcon(icon_path))
        self.TBMinButton.setIconSize(QSize(25, 25))
        self.TBMinButton.setFixedHeight(titleBarHeight)
        self.TBMinButton.setFixedWidth(titleBarHeight+10)
        self.TBMinButton.setObjectName("titleBarButton")

        self.maximizeIcon = QIcon(os.path.join(SCRIPT_DIR, "maximize.svg"))
        self.normalizeIcon = QIcon(os.path.join(SCRIPT_DIR, "normalize.svg"))
        self.TBMaxButton.setIcon(self.maximizeIcon)
        self.TBMaxButton.setIconSize(QSize(22, 22))
        self.TBMaxButton.setFixedHeight(titleBarHeight)
        self.TBMaxButton.setFixedWidth(titleBarHeight+10)
        self.TBMaxButton.setObjectName("titleBarButton")

        icon_path = os.path.join(SCRIPT_DIR, "close.svg")
        self.TBCloseButton.setIcon(QIcon(icon_path))
        self.TBCloseButton.setIconSize(QSize(25, 25))
        self.TBCloseButton.setFixedHeight(titleBarHeight)
        self.TBCloseButton.setFixedWidth(titleBarHeight+10)
        self.TBCloseButton.setObjectName("titleBarButton")

        self.userInputLayout.setContentsMargins(20,20,20,20)

        self.workingAreaLimiter.setFixedWidth(2)
        self.workingAreaLimiter.setObjectName("limiter")

        self.qrCodeLayout.setContentsMargins(20,20,20,20)

        self.userInputTitle.setObjectName("userInputTitle")

        self.textEntryTitle.setObjectName("textEntryTitle")

        self.textEntry.setMinimumHeight(20)
        self.textEntry.setMaximumHeight(200)
        self.textEntry.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        length = self.height()-200
        self.qrCode.setFixedSize(length, length)

        self.qrCodeButtonsLayout.setContentsMargins(0, 20, 0, 0)
        
        self.generateButton.setFixedSize(length-110, 50)
        self.generateButton.setObjectName("QRButton")

        icon_path = os.path.join(SCRIPT_DIR, "download.svg")
        self.downloadButton.setIcon(QIcon(icon_path))
        self.downloadButton.setIconSize(QSize(32, 32))
        self.downloadButton.setFixedSize(50, 50)
        self.downloadButton.setObjectName("QRButton")
        self.downloadButton.setProperty("size", "small")

        icon_path = os.path.join(SCRIPT_DIR, "copy.svg")
        self.copyButton.setIcon(QIcon(icon_path))
        self.copyButton.setIconSize(QSize(32, 32))
        self.copyButton.setFixedSize(50, 50)
        self.copyButton.setObjectName("QRButton")
        self.copyButton.setProperty("style", "small")

        with open(".\\style.qss", mode="r", encoding="utf-8") as style:
            self.setStyleSheet(style.read())
        
    def _calculateWindowGeometry(self) -> tuple[QPoint,int,int]:
        '''Creates some constants used for UI creation.'''
        availableSpace = self.screen().availableGeometry()
        SCREENW = availableSpace.width()
        SCREENH = availableSpace.height()
        HEIGHT = int(SCREENH*0.9)
        WIDTH = int(SCREENW*0.7)
        X = SCREENW//2-WIDTH//2
        Y = SCREENH//2-HEIGHT//2
        return QPoint(X, Y), WIDTH, HEIGHT
   
class TitleBar(QWidget):
    def __init__(self, parent):
        '''Initializes the top bar widget.'''
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.oldClickPos = None
        self.newClickPos = None

    def mousePressEvent(self, event) -> None:
        '''Triggered when the title bar is clicked by the mouse.'''
        if event.button() == Qt.MouseButton.LeftButton:
            self.setMouseTracking(True)
            self.oldClickPos = event.position()
    
    def mouseReleaseEvent(self, event) -> None:
        '''Triggered when the title bar is released by the mouse.'''
        if event.button() == Qt.MouseButton.LeftButton:
            self.setMouseTracking(False)
            self.oldClickPos = None
    
    def mouseMoveEvent(self, event) -> None:
        '''Triggered when the mouse moves over the title bar'''
        if not(self.oldClickPos == None):
            window = self.window()
            if (event.buttons() == Qt.MouseButton.LeftButton) and not(window.isMinimized()):
                if (window.isMaximized()) or (window.windowIsMaximized):
                    self.newClickPos = event.position()
                    coefs: tuple[float, float] = (
                        self.newClickPos.x()/window.width(), 
                        self.newClickPos.y()/window.height()
                    )
                    window.maximize(event)
                    self.oldClickPos = QPointF(window.width()*coefs[0], window.height()*coefs[1])
                    newPos = QCursor.pos() - self.oldClickPos.toPoint()
                    window.normalPos = newPos
                    window.move(window.normalPos.x(), window.normalPos.y())
                else:
                    self.newClickPos = event.position()
                    mousePos = QCursor.pos()
                    availableHeight = self.screen().availableGeometry().height()
                    if (mousePos.y() > availableHeight):
                        QCursor.setPos(mousePos.x(), availableHeight)
                        self.newClickPos.setY(availableHeight)
                    delta = self.newClickPos - self.oldClickPos
                    newPos = window.normalPos + delta.toPoint()
                    window.normalPos = newPos
                    window.move(window.normalPos.x(), window.normalPos.y())

    def mouseDoubleClickEvent(self, event) -> None:
        '''Triggered when the title bar is double clicked by the mouse.'''
        if event.button() == Qt.MouseButton.LeftButton:
            self.window().maximize(event)




class QRWidget(QWidget):
    def __init__(self):
        '''Initializes the widget that displays the QR Code.'''
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.text = ''

if __name__ == '__main__':
    program = Program()
    program.execute()