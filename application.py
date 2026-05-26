"""
Done using no pre-made modules for qr code creation such as qrcode, pyqrcode, or other.
Any and all classes for qr code creation were coded by myself, only few snippets may have come from
the internet, which were then adapted for this code specifically.

This was made as a proof of skill and knowledge in both simple app making (with GUI), tinkering
with data (creating the QR CODE itself), and general Python knowledge.

Lots of credits go to the guide found on this website, which explains the process very clearly: 
https://www.thonky.com/qr-code-tutorial/

Began on March 10th 2026.
Slowed down progress from April 6th 2026 to April 27th 2026
"""
import os
import sys
import ctypes
from math import log
from itertools import combinations
from typing import Any, override
from time import sleep, time
from qrworker import QRWorker
from qrerrors import QRError
from IPC_coms import QRMessage, QRTask, QRResult
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QButtonGroup,
    QTextEdit,
    QWidget,
    QMenu,
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
    QAction,
    QPixmap,
    QCursor,
)
from PyQt6.QtCore import (
    Qt, 
    QSize,
    QPoint,
    QPointF,
    QRect,
    QTimer,
)
from multiprocessing import (
    Process,
    Queue,
    freeze_support,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("stoomy.qrcodegen")


class Program:
    '''Wrapper class for the window and application instances.'''
    def __init__(self):
        self.app = Application(self)
        self.window = Window(self)
    
    def execute(self) -> None:
        '''Executes the program.'''
        self.window.show()
        self.app.createQRProcess()
        self.app.exec()

class Application(QApplication):
    def __init__(self, program: Program):
        super().__init__([])
        self.program: Program = program
        self.taskQueue: Queue = Queue()
        self.resultQueue: Queue = Queue()
        self.checkTimer: QTimer = QTimer(self)
        self.checkTimer.timeout.connect(self.checkQueue)
        self.qrProcessStart: None | float = None
    
    def createQRProcess(self) -> None:
        '''Creates and starts the QRProcess.'''
        self.program.window.qrCodeText.setText('Please wait...')
        self.qrWorker: QRWorker = QRWorker(self.taskQueue, self.resultQueue)
        self.qrProcess: Process = Process(target=self.qrWorker.idle, daemon=True)
        self.qrProcess.start()
        self.startCheckingQueue()
    
    def terminateQRProcess(self) -> None:
        '''Properly terminates the QR Process and everything related.'''
        self.stopCheckingQueue()
        self.qrProcess.terminate()
        self.qrWorker.resetClass()
    
    def restartQRProcess(self) -> None:
        '''Restarts the QRProcess.'''
        self.terminateQRProcess()
        self.createQRProcess()
    
    def startGeneration(self) -> None:
        '''Tells the QRProcess to start generating the QR Code's qrCodeData'''
        window: Window = self.program.window
        window.disableQRCodeLayout()
        text: str = window.textEntry.toPlainText()
        if (text == ''):
            print('Text cannot be empty!')
            window.enableQRCodeLayout()
            return
        ecLevel: int = window.ecButtonGroup.checkedId()
        self.taskQueue.put(QRTask(QRWorker.generateQRCode, args=(text, ecLevel)))
        window.qrCodeText.setText('Loading...')
        # this line is temporary, will change for the loading icon later.
        self.startCheckingQueue()
        
    def startCheckingQueue(self) -> None:
        '''Starts repeatedly checking the resultQueue.'''
        self.qrProcessStart = time()
        self.checkTimer.start(100)
    
    def checkQueue(self) -> None:
        '''Checks the resultQueue once to see whether the QRWorker has sent back something or not.'''
        PROCESS_TIMEOUT_TIME: int = 10
        if not(self.resultQueue.empty()):
            response: QRMessage | QRResult = self.resultQueue.get()
            if (isinstance(response, QRMessage)):
                if (response == QRMessage.ProcessStarted):
                    window: Window = self.program.window
                    window.enableQRCodeLayout()
                    window.qrCodeText.setText('Waiting for input...')
                    print('Successfully started QRWorker!')
            elif (isinstance(response, QRResult)):
                if (response.wasSuccessful):
                    print('No errors occured during generation.')
                else:
                    # An error occured.
                    error: QRError = response.error
                    if (error is QRError.ModeError):
                        failedChar: str = response.data
                        print(failedChar + ' cannot be encoded using any of the four available modes!')
                    elif (error is QRError.VersionError):
                        print('Too much data to encode!')
                        # alert the user about this here
                    elif (error is QRError.EncodeError):
                        print('An error occured trying to encode the text!')
                self.program.window.enableQRCodeLayout()
            self.stopCheckingQueue()
        elif (time() - self.qrProcessStart > PROCESS_TIMEOUT_TIME):
            print('Process timed out!')
            self.restartQRProcess()
    
    def stopCheckingQueue(self) -> None:
        '''Stops checking the resultQueue.'''
        self.checkTimer.stop()
        self.qrProcessStart = None

class Window(QWidget):
    def __init__(self, program: Program):
        '''Initializes the UI for the application.'''
        super().__init__()
        self.program: Program = program
        self._setupWindowGeometry()
        self._createTitleBarWidgets()
        self._createWorkingAreaWidgets()
        self._initLayout()
        self._placeAllWidgets()
        self._setBackgroundColor((26, 12, 32))
        self._stylizeWidgets()
    
    def isTrueMaximized(self) -> bool:
        '''
        Use of the self.windowIsMaximized attribute fix :\n
        Returns True if the window is maximized, False if not.
        This method returns the correct value even if the window has been or is currently minimized, which self.isMaximized() does not. 
        If the self.windowIsMaximized attribute hasn't been defined when this method is executed, it will return self.isMaximized().
        '''
        if hasattr(self, 'windowIsMaximized'):
            return (self.isMaximized()) or (self.windowIsMaximized)
        else:
            return (self.isMaximized())
    
    def disableQRCodeLayout(self) -> None:
        '''Disables the QR Code area's widgets.'''
        self.generateButton.setEnabled(False)
        self.downloadButton.setEnabled(False)
        self.copyButton.setEnabled(False)
        # add loading icon on qrcode here
    
    def enableQRCodeLayout(self) -> None:
        '''Enables the QR Code area's widgets.'''
        self.generateButton.setEnabled(True)
        self.downloadButton.setEnabled(True)
        self.copyButton.setEnabled(True)
        # remove loading icon on qrcode here
    
    def maximize(self, *args: Any) -> None:
        '''Triggered when TBMaxButton is pressed, or when the title bar is double clicked'''
        if (self.isTrueMaximized()):
            self.windowIsMaximized = False
            self.showNormal()
            self.setGeometry(self.normalPos.x(), self.normalPos.y(), self.normalWidth, self.normalHeight)
            self.TBMaxButton.setIcon(self.maximizeIcon)
        else:
            self.windowIsMaximized = True
            self.showMaximized()
            self.TBMaxButton.setIcon(self.normalizeIcon)
        self.switchWindowEdges()

    def showEvent(self, event) -> None:
        '''Triggered when the window is shown on the screen'''
        super().showEvent(event)
        self.switchWindowEdges()
    
    def switchWindowEdges(self) -> None:
        '''Communicates with the Windows DWM API to switch the window's borders and corners between rounded and not'''
        if sys.platform == "win32":
            hwnd = int(self.winId())
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            if (self.isTrueMaximized()):
                DWMWCP_ROUND = 1
            else:
                DWMWCP_ROUND = 2
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_WINDOW_CORNER_PREFERENCE,
                ctypes.byref(ctypes.c_int(DWMWCP_ROUND)),
                ctypes.sizeof(ctypes.c_int)
            )
    
    def loadIcon(self, path: str) -> QIcon:
        '''Generates the QIcon used as the app's icon in the taskbar and such.'''
        icon: QIcon = QIcon()
        source: QPixmap = QPixmap(path)
        for size in range(1, 257):
            # I'm generating 256 different icons of resolution (size, size) just so I can be free of mind
            scaled: QPixmap = source.scaled(
                size, size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation
            )
            icon.addPixmap(scaled)
        return icon

    def _setupWindowGeometry(self) -> None:
        '''Creates and sets up the window geometry.'''
        self.windowIsMaximized = False
        # This variable is used to remember whether the window was maximized or not after it gets minimized, as self.isMaximized() doesn't return the correct
        # value whenever the window is minimized while being maximized.
        self.normalPos, self.normalWidth, self.normalHeight = self._calculateWindowGeometry()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        #self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(self.normalPos.x(), self.normalPos.y(), self.normalWidth, self.normalHeight)

    def _initLayout(self) -> None:
        '''Initializes all the layouts that will automatically arrange all the widgets in the window.'''
        self.outerLayout = QVBoxLayout()

        self.titleBarLayout = QHBoxLayout()
        
        self.workingAreaLayout = QHBoxLayout()
        
        self.userInputLayout = QWidget()
        self.userInputLayout.setLayout(QVBoxLayout())

        self.textEntryLayout = QWidget()
        self.textEntryLayout.setLayout(QVBoxLayout())

        self.ecButtonLayout = QWidget()
        self.ecButtonLayout.setLayout(QVBoxLayout())

        self.qrCodeLayout = QWidget()
        self.qrCodeLayout.setLayout(QVBoxLayout())

        self.qrCodeButtonsLayout = QHBoxLayout()

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

        self.firstLimiter = QWidget()

        self.textEntryTitle = QLabel("Text :")

        self.textEntry = QTextEdit()
        self.textEntry.setPlaceholderText("Text to encode goes here...")
        self.textEntry.setAcceptRichText(False)
        self.textEntry.setReadOnly(False)

        self.secondLimiter = QWidget()

        self.ecButtonGroupTitle = QLabel("Error Correction Level :")
        
        self.ecLowButton = QPushButton("Level L (Low) : Up to 7% data recovery.")
        self.ecMediumButton = QPushButton("Level M (Medium) : Up to 15% data recovery.")
        self.ecQuartileButton = QPushButton("Level Q (Quartile) : Up to 25% data recovery.")
        self.ecHighButton = QPushButton("Level H (High) : Up to 30% data recovery.")

        self.ecButtonGroup = QButtonGroup()
        self.ecButtonGroup.addButton(self.ecLowButton, 1)
        self.ecButtonGroup.addButton(self.ecMediumButton, 2)
        self.ecButtonGroup.addButton(self.ecQuartileButton, 3)
        self.ecButtonGroup.addButton(self.ecHighButton, 4)
        for button in self.ecButtonGroup.buttons():
            button.setCheckable(True)
        self.ecMediumButton.setChecked(True)

        self.workingAreaLimiter = QWidget()

        self.qrCode = QRWidget()
        self.qrCode.setLayout(QVBoxLayout())

        self.qrCodeText = QLabel()

        self.qrCodeLoadingIcon = QLabel()

        self.generateButton = QPushButton("Generate")
        self.generateButton.setAutoDefault(False)
        self.generateButton.clicked.connect(self.program.app.startGeneration)

        self.downloadButton = QPushButton()
        self.downloadButton.setAutoDefault(False)

        self.copyButton = QPushButton()
        self.copyButton.setAutoDefault(False)

        self.disableQRCodeLayout()

    def _placeAllWidgets(self) -> None:
        '''Places all the widgets into their respective layouts/positions.'''
        self.setLayout(self.outerLayout)

        self.outerLayout.addWidget(self.titleBar)
        self.outerLayout.addWidget(self.outerLimiter)
        self.outerLayout.addLayout(self.workingAreaLayout)

        self.titleBar.setLayout(self.titleBarLayout)
        self.titleBarLayout.addWidget(self.appIcon)
        self.titleBarLayout.addWidget(self.appTitle)
        self.titleBarLayout.addWidget(self.TBMinButton)
        self.titleBarLayout.addWidget(self.TBMaxButton)
        self.titleBarLayout.addWidget(self.TBCloseButton)

        self.workingAreaLayout.addWidget(self.userInputLayout)
        self.workingAreaLayout.addWidget(self.workingAreaLimiter)
        self.workingAreaLayout.addWidget(self.qrCodeLayout)
        
        userInputLayout: QVBoxLayout = self.userInputLayout.layout()
        userInputLayout.addWidget(self.userInputTitle)
        userInputLayout.addWidget(self.firstLimiter)
        userInputLayout.addWidget(self.textEntryLayout)
        userInputLayout.addWidget(self.secondLimiter)
        userInputLayout.addWidget(self.ecButtonLayout)
        
        textEntryLayout: QVBoxLayout = self.textEntryLayout.layout()
        textEntryLayout.addWidget(self.textEntryTitle)
        textEntryLayout.addWidget(self.textEntry)

        ecButtonLayout: QVBoxLayout = self.ecButtonLayout.layout()
        ecButtonLayout.addWidget(self.ecButtonGroupTitle)

        for button in self.ecButtonGroup.buttons():
            ecButtonLayout.addWidget(button)

        qrCode: QVBoxLayout = self.qrCode.layout()
        qrCode.addWidget(self.qrCodeText)
        qrCode.addWidget(self.qrCodeLoadingIcon)

        qrCodeLayout: QVBoxLayout = self.qrCodeLayout.layout()
        qrCodeLayout.addWidget(self.qrCode)
        qrCodeLayout.addLayout(self.qrCodeButtonsLayout)

        self.qrCodeButtonsLayout.addWidget(self.generateButton)
        self.qrCodeButtonsLayout.addWidget(self.downloadButton)
        self.qrCodeButtonsLayout.addWidget(self.copyButton)
    
    def _setBackgroundColor(self, backgroundColor: tuple[int, int, int]) -> None:
        '''Sets the color of the main window's background to the specified RGB color.'''
        palette: QPalette = self.palette()
        color: QColor = QColor(*backgroundColor)
        palette.setColor(QPalette.ColorRole.Window, color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)
    
    def _stylizeWidgets(self) -> None:
        '''Applies all of the style to all the widgets/layouts'''
        iconPath: str = os.path.join(SCRIPT_DIR, r"runtime-icon.png")
        self.setWindowIcon(self.loadIcon(iconPath))
        self.setWindowTitle('QR Code Generator - Waiting')

        titleBarHeight: int = self.titleBar.height()

        self.outerLayout.setContentsMargins(0, 0, 0, 0)
        self.outerLayout.setSpacing(0)

        self.titleBarLayout.setContentsMargins(0, 0, 0, 0)
        self.titleBarLayout.setSpacing(0)

        iconPath = os.path.join(SCRIPT_DIR, r"titlebar-icon.svg")
        self.appIcon.setPixmap(QPixmap(iconPath).scaled(25, 25))
        self.appIcon.setContentsMargins(15,0,15,0)
        self.appIcon.setFixedWidth(60) 

        iconPath = os.path.join(SCRIPT_DIR, "minimize.svg")
        self.minimizeIcon: QIcon = QIcon(iconPath)
        self.TBMinButton.setIcon(self.minimizeIcon)
        self.TBMinButton.setIconSize(QSize(25, 25))
        self.TBMinButton.setFixedHeight(titleBarHeight)
        self.TBMinButton.setFixedWidth(titleBarHeight+10)
        self.TBMinButton.setObjectName("titleBarButton")

        iconPath = os.path.join(SCRIPT_DIR, "maximize.svg")
        self.maximizeIcon: QIcon = QIcon(iconPath)
        iconPath = os.path.join(SCRIPT_DIR, "normalize.svg")
        self.normalizeIcon: QIcon = QIcon(iconPath)
        self.TBMaxButton.setIcon(self.maximizeIcon)
        self.TBMaxButton.setIconSize(QSize(22, 22))
        self.TBMaxButton.setFixedHeight(titleBarHeight)
        self.TBMaxButton.setFixedWidth(titleBarHeight+10)
        self.TBMaxButton.setObjectName("titleBarButton")

        iconPath = os.path.join(SCRIPT_DIR, "close.svg")
        self.closeIcon: QIcon = QIcon(iconPath)
        self.TBCloseButton.setIcon(self.closeIcon)
        self.TBCloseButton.setIconSize(QSize(25, 25))
        self.TBCloseButton.setFixedHeight(titleBarHeight)
        self.TBCloseButton.setFixedWidth(titleBarHeight+10)
        self.TBCloseButton.setObjectName("titleBarButton")

        self.outerLimiter.setFixedHeight(1)
        self.outerLimiter.setObjectName("limiter")

        self.workingAreaLayout.setContentsMargins(0, 0, 0, 0)
        self.workingAreaLayout.setSpacing(0)

        userInputLayout: QVBoxLayout = self.userInputLayout.layout()
        userInputLayout.setContentsMargins(0, 0, 0, 0)
        userInputLayout.setSpacing(0)

        self.userInputTitle.setMinimumHeight(100)
        self.userInputTitle.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Maximum)
        self.userInputTitle.setObjectName("userInputTitle")

        self.firstLimiter.setFixedHeight(1)
        self.firstLimiter.setObjectName("limiter")

        textEntryLayout: QVBoxLayout = self.textEntryLayout.layout()
        textEntryLayout.setContentsMargins(20, 0, 20, 0)
        textEntryLayout.setSpacing(0)
        self.textEntryLayout.setObjectName("textEntryLayout")

        self.textEntryTitle.setObjectName("textEntryTitle")

        self.textEntry.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.textEntry.setObjectName("textEntry")

        self.secondLimiter.setFixedHeight(1)
        self.secondLimiter.setObjectName("limiter")

        ecButtonLayout: QVBoxLayout = self.ecButtonLayout.layout()
        ecButtonLayout.setContentsMargins(20, 0, 20, 40)
        ecButtonLayout.setSpacing(0)

        self.ecButtonGroupTitle.setObjectName("ecTitle")

        for button in self.ecButtonGroup.buttons():
            button.setObjectName("ecButton")
        self.ecHighButton.setProperty("position", "last")

        self.workingAreaLimiter.setFixedWidth(1)
        self.workingAreaLimiter.setObjectName("limiter")

        qrCodeLayout: QVBoxLayout = self.qrCodeLayout.layout()
        qrCodeLayout.setContentsMargins(20, 0, 20, 0)
        qrCodeLayout.setSpacing(0)

        length: int = self.height()-200
        self.qrCode.setFixedSize(length, length)
        self.qrCode.setProperty("state", "empty")

        self.qrCodeText.setObjectName("QRCodeText")
        self.qrCodeText.setStyleSheet(f"font-size: {length/15}px")

        iconPath = os.path.join(SCRIPT_DIR, "loading.svg")
        size: int = int(length/3)
        self.qrCodeLoadingIcon.setPixmap(QPixmap(iconPath).scaled(size,size))
        self.qrCodeLoadingIcon.hide()

        self.qrCodeButtonsLayout.setContentsMargins(0, 20, 0, 0)
        self.qrCodeButtonsLayout.setSpacing(0)
        
        self.generateButton.setFixedSize(length-110, 50)
        self.generateButton.setObjectName("QRButton")

        iconPath = os.path.join(SCRIPT_DIR, "download.svg")
        self.downloadButton.setIcon(QIcon(iconPath))
        self.downloadButton.setIconSize(QSize(32, 32))
        self.downloadButton.setFixedSize(50, 50)
        self.downloadButton.setObjectName("QRButton")
        self.downloadButton.setProperty("style", "small")

        iconPath = os.path.join(SCRIPT_DIR, "copy.svg")
        self.copyButton.setIcon(QIcon(iconPath))
        self.copyButton.setIconSize(QSize(32, 32))
        self.copyButton.setFixedSize(50, 50)
        self.copyButton.setObjectName("QRButton")
        self.copyButton.setProperty("style", "small")

        stylePath: str = os.path.join(SCRIPT_DIR, "style.qss")
        with open(stylePath, mode="r", encoding="utf-8") as style:
            self.setStyleSheet(style.read())
        
    def _calculateWindowGeometry(self) -> tuple[QPoint,int,int]:
        '''Creates some constants used for UI creation.'''
        availableSpace: QRect = self.screen().availableGeometry()
        SCREENW: int = availableSpace.width()
        SCREENH: int = availableSpace.height()
        HEIGHT: int = int(SCREENH*0.9)
        WIDTH: int = int(SCREENW*0.7)
        X: float = SCREENW//2-WIDTH//2
        Y: float = SCREENH//2-HEIGHT//2
        return QPoint(X, Y), WIDTH, HEIGHT

class QRWidget(QWidget):
    def __init__(self) -> None:
        '''Initializes the special QWidget that displays the QR Code.'''
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.qrCodeData: None | Unknown = None

    def paintQRCode(self) -> None:
        '''Paints the QR Code onto the widget, as long as there is qrCodeData to use.'''
        raise NotImplementedError()

class TitleBar(QWidget):
    def __init__(self, parent: Window) -> None:
        '''Initializes the top bar widget.'''
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.oldClickPos = None
        self.newClickPos = None

    @override
    def mousePressEvent(self, event) -> None:
        '''Triggered when the title bar is clicked by the mouse.'''
        if (event.button() == Qt.MouseButton.LeftButton):
            self.setMouseTracking(True)
            self.oldClickPos = QCursor.pos()
            self.windowStartPos = self.window().normalPos
    
    @override
    def mouseReleaseEvent(self, event) -> None:
        '''Triggered when the title bar is released by the mouse.'''
        if (event.button() == Qt.MouseButton.LeftButton):
            self.setMouseTracking(False)
            self.oldClickPos: None | QPoint = None
            self.windowStartPos: None | QPoint = None

    @override
    def mouseMoveEvent(self, event) -> None:
        '''Triggered when the mouse moves over the title bar'''
        if not(self.oldClickPos == None):
            window: Window = self.window()
            if (event.buttons() == Qt.MouseButton.LeftButton) and not(window.isMinimized()):
                if (window.isMaximized()) or (window.windowIsMaximized):
                    mousePos: QPoint = QCursor.pos()
                    coefs: tuple[float, float] = (
                        mousePos.x()/self.width(), 
                        mousePos.y()/self.height()
                    )
                    window.maximize(event)
                    newPos: QPoint = mousePos - QPointF(self.width()*coefs[0], self.height()*coefs[1]).toPoint()
                    window.normalPos = newPos
                    window.move(window.normalPos.x(), window.normalPos.y())
                    self.oldClickPos = QCursor.pos()
                    self.windowStartPos = window.normalPos
                else:
                    mousePos: QPoint = QCursor.pos()
                    availableHeight: int = self.screen().availableGeometry().height()
                    if (mousePos.y() > availableHeight):
                        QCursor.setPos(mousePos.x(), availableHeight)
                    delta: QPoint = mousePos - self.oldClickPos
                    newPos: QPoint = self.windowStartPos + delta
                    window.normalPos = newPos
                    window.move(window.normalPos.x(), window.normalPos.y())

    @override
    def mouseDoubleClickEvent(self, event) -> None:
        '''Triggered when the title bar is double clicked by the mouse.'''
        if event.button() == Qt.MouseButton.LeftButton:
            self.window().maximize(event)
    
    @override
    def contextMenuEvent(self, event) -> None:
        '''Triggered when the titlebar's is right clicked.'''
        window: Window = self.window()
        menu: QMenu = QMenu(self)
        normAction: QAction = QAction(window.normalizeIcon, "Restore", parent=self)
        maxAction: QAction = QAction(window.maximizeIcon, "Maximize", parent=self)
        if (window.isTrueMaximized()):
            normAction.triggered.connect(window.maximize)
            maxAction.setEnabled(False)
        else:
            maxAction.triggered.connect(window.maximize)
            normAction.setEnabled(False)
        minAction: QAction = QAction(window.minimizeIcon, "Minimize", parent=self)
        minAction.triggered.connect(window.showMinimized)
        closeAction: QAction = QAction(window.closeIcon, "Close", parent=self)
        closeAction.setShortcut('Alt+F4')
        closeAction.triggered.connect(window.close)
        menu.addActions((normAction, minAction, maxAction))
        menu.addSeparator()
        menu.addAction(closeAction)
        menu.exec(event.globalPos())

if __name__ == '__main__':
    freeze_support()
    Program().execute()