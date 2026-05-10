"""
Done using no pre-made modules for qr code creation such as qrcode, pyqrcode, or other.
Any and all classes for qr code creation were coded by myself, only few snippets may have come from
the internet, which were then adapted for this code specifically.

This was made as a proof of skill and knowledge in both simple app making (with GUI), tinkering
with data (creating the QR CODE itself), and general Python knowledge.

Began on March 10th 2026.
Slowed down progress from April 6th 2026 to April 27th 2026
"""
import os
import sys
import ctypes
import qrdata
from typing import Self, Any, override
from dataclasses import dataclass
from time import sleep, time, perf_counter
from enum import Enum, auto
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
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
        self.qrWorker: QRWorker = QRWorker(self.taskQueue, self.resultQueue)
        self.qrProcess: Process = Process(target=self.qrWorker.standby, daemon=True)
        self.qrProcess.start()
        self.startCheckingQueue()
    
    def terminateQRProcess(self) -> None:
        '''Properly terminates the QR Process and everything related.'''
        self.stopCheckingQueue()
        self.qrProcess.terminate()
        self.qrWorker.resetClass()
        self.program.window.enableQRCodeLayout()
        return 
    
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
        self.taskQueue.put((text, ecLevel))
        self.startCheckingQueue()
        
    def startCheckingQueue(self) -> None:
        '''Starts repeatedly checking the resultQueue.'''
        self.qrProcessStart = time()
        self.checkTimer.start(100)
    
    def checkQueue(self) -> None:
        '''Checks the resultQueue once to see whether the QRWorker has sent back something or not.'''
        if (time() - self.qrProcessStart > 10):
            print('Process timed out!')
            self.restartQRProcess()
        elif not(self.resultQueue.empty()):
            response: QRRe = self.resultQueue.get()
            if ():
                # No errors, normal response.
                if (response.success):
                    # QRWorker has successfully started.
                    window: Window = self.program.window
                    window.enableQRCodeLayout()
                    window.qrCodeText.setText('Waiting for input...')
                    print('Successfully started QRWorker!')
                else:
                    print('No errors occured during generation.')
            elif (isinstance(qrCodeData, tuple)):
                # An error occured, qrCodeData: tuple[errorCode: int, any number of elements of any type].
                errorCode: int = qrCodeData[0]
                if (errorCode == QRError.ModeError.value):
                    # Error trying to find encoding mode of a character. 
                    # qrCodeData: tuple[errorCode, ord(char)]
                    failedChar: str = chr(qrCodeData[1])
                    print(failedChar + ' cannot be encoded using any of the four available modes!')
                elif (errorCode == QRError.EncodeError.value):
                    # Error during encoding of the text.
                    print('An error occured trying to encode the text!')
            self.stopCheckingQueue()
            self.program.window.enableQRCodeLayout()
    
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
        if (self.isMaximized()) or (self.windowIsMaximized):
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

        self.qrCodeText = QLabel("Please wait...")

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
        
        userInputLayout = self.userInputLayout.layout()
        userInputLayout.addWidget(self.userInputTitle)
        userInputLayout.addWidget(self.firstLimiter)
        userInputLayout.addWidget(self.textEntryLayout)
        userInputLayout.addWidget(self.secondLimiter)
        userInputLayout.addWidget(self.ecButtonLayout)
        
        textEntryLayout = self.textEntryLayout.layout()
        textEntryLayout.addWidget(self.textEntryTitle)
        textEntryLayout.addWidget(self.textEntry)

        ecButtonLayout = self.ecButtonLayout.layout()
        ecButtonLayout.addWidget(self.ecButtonGroupTitle)

        for button in self.ecButtonGroup.buttons():
            ecButtonLayout.addWidget(button)

        qrCode = self.qrCode.layout()
        qrCode.addWidget(self.qrCodeText)
        qrCode.addWidget(self.qrCodeLoadingIcon)

        qrCodeLayout = self.qrCodeLayout.layout()
        qrCodeLayout.addWidget(self.qrCode)
        qrCodeLayout.addLayout(self.qrCodeButtonsLayout)

        self.qrCodeButtonsLayout.addWidget(self.generateButton)
        self.qrCodeButtonsLayout.addWidget(self.downloadButton)
        self.qrCodeButtonsLayout.addWidget(self.copyButton)
    
    def _setBackgroundColor(self, backgroundColor: tuple[int, int, int]) -> None:
        '''Sets the color of the main window's background to the specified RGB color.'''
        palette = self.palette()
        color = QColor(*backgroundColor)
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

        iconPath: str = os.path.join(SCRIPT_DIR, "minimize.svg")
        self.TBMinButton.setIcon(QIcon(iconPath))
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

        iconPath: str = os.path.join(SCRIPT_DIR, "close.svg")
        self.TBCloseButton.setIcon(QIcon(iconPath))
        self.TBCloseButton.setIconSize(QSize(25, 25))
        self.TBCloseButton.setFixedHeight(titleBarHeight)
        self.TBCloseButton.setFixedWidth(titleBarHeight+10)
        self.TBCloseButton.setObjectName("titleBarButton")

        self.outerLimiter.setFixedHeight(1)
        self.outerLimiter.setObjectName("limiter")

        self.workingAreaLayout.setContentsMargins(0, 0, 0, 0)
        self.workingAreaLayout.setSpacing(0)

        userInputLayout = self.userInputLayout.layout()
        userInputLayout.setContentsMargins(0, 0, 0, 0)
        userInputLayout.setSpacing(0)

        self.userInputTitle.setMinimumHeight(100)
        self.userInputTitle.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Maximum)
        self.userInputTitle.setObjectName("userInputTitle")

        self.firstLimiter.setFixedHeight(1)
        self.firstLimiter.setObjectName("limiter")

        textEntryLayout = self.textEntryLayout.layout()
        textEntryLayout.setContentsMargins(20, 0, 20, 0)
        textEntryLayout.setSpacing(0)
        self.textEntryLayout.setObjectName("textEntryLayout")

        self.textEntryTitle.setObjectName("textEntryTitle")

        self.textEntry.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.textEntry.setObjectName("textEntry")

        self.secondLimiter.setFixedHeight(1)
        self.secondLimiter.setObjectName("limiter")

        ecButtonLayout = self.ecButtonLayout.layout()
        ecButtonLayout.setContentsMargins(20, 0, 20, 40)
        ecButtonLayout.setSpacing(0)

        self.ecButtonGroupTitle.setObjectName("ecTitle")

        for button in self.ecButtonGroup.buttons():
            button.setObjectName("ecButton")
        self.ecHighButton.setProperty("position", "last")

        self.workingAreaLimiter.setFixedWidth(1)
        self.workingAreaLimiter.setObjectName("limiter")

        layout = self.qrCodeLayout.layout()
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(0)

        length = self.height()-200
        self.qrCode.setFixedSize(length, length)
        self.qrCode.setProperty("state", "empty")

        self.qrCodeText.setObjectName("QRCodeText")
        self.qrCodeText.setStyleSheet(f"font-size: {length/15}px")

        iconPath: str = os.path.join(SCRIPT_DIR, "loading.svg")
        size = int(length/3)
        self.qrCodeLoadingIcon.setPixmap(QPixmap(iconPath).scaled(size,size))
        self.qrCodeLoadingIcon.hide()

        self.qrCodeButtonsLayout.setContentsMargins(0, 20, 0, 0)
        self.qrCodeButtonsLayout.setSpacing(0)
        
        self.generateButton.setFixedSize(length-110, 50)
        self.generateButton.setObjectName("QRButton")

        iconPath: str = os.path.join(SCRIPT_DIR, "download.svg")
        self.downloadButton.setIcon(QIcon(iconPath))
        self.downloadButton.setIconSize(QSize(32, 32))
        self.downloadButton.setFixedSize(50, 50)
        self.downloadButton.setObjectName("QRButton")
        self.downloadButton.setProperty("style", "small")

        iconPath: str = os.path.join(SCRIPT_DIR, "copy.svg")
        self.copyButton.setIcon(QIcon(iconPath))
        self.copyButton.setIconSize(QSize(32, 32))
        self.copyButton.setFixedSize(50, 50)
        self.copyButton.setObjectName("QRButton")
        self.copyButton.setProperty("style", "small")

        stylePath = os.path.join(SCRIPT_DIR, "style.qss")
        with open(stylePath, mode="r", encoding="utf-8") as style:
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

class QRWidget(QWidget):
    def __init__(self) -> None:
        '''Initializes the special QWidget that displays the QR Code.'''
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.qrCodeData = None

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
            self.oldClickPos = None
            self.windowStartPos = None
    
    @override
    def mouseMoveEvent(self, event) -> None:
        '''Triggered when the mouse moves over the title bar'''
        if not(self.oldClickPos == None):
            window = self.window()
            if (event.buttons() == Qt.MouseButton.LeftButton) and not(window.isMinimized()):
                if (window.isMaximized()) or (window.windowIsMaximized):
                    mousePos = QCursor.pos()
                    coefs: tuple[float, float] = (
                        mousePos.x()/self.width(), 
                        mousePos.y()/self.height()
                    )
                    window.maximize(event)
                    newPos = mousePos - QPointF(self.width()*coefs[0], self.height()*coefs[1]).toPoint()
                    window.normalPos = newPos
                    window.move(window.normalPos.x(), window.normalPos.y())
                    self.oldClickPos = QCursor.pos()
                    self.windowStartPos = self.window().normalPos
                else:
                    mousePos = QCursor.pos()
                    availableHeight = self.screen().availableGeometry().height()
                    if (mousePos.y() > availableHeight):
                        QCursor.setPos(mousePos.x(), availableHeight)
                    delta = mousePos - self.oldClickPos
                    newPos = self.windowStartPos + delta
                    window.normalPos = newPos
                    window.move(window.normalPos.x(), window.normalPos.y())

    @override
    def mouseDoubleClickEvent(self, event) -> None:
        '''Triggered when the title bar is double clicked by the mouse.'''
        if event.button() == Qt.MouseButton.LeftButton:
            self.window().maximize(event)

class QRWorker:
    '''Class whose instance is ran in another process to generate the QR Code's qrCodeData.'''
    _instance: None | Self = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs) -> Self:
        '''Ensures only one QRWorker can exist at a time.'''
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        if (__name__ == '__main__'):
            return cls._instance

    def __init__(self, taskQueue: Queue, resultQueue: Queue) -> None:
        '''Initializes the QRWorker.'''
        if self.__class__._initialized:
            print('Can only create one QRWorker at a time!')
            return
        else:
            self.taskQueue: Queue = taskQueue
            self.resultQueue: Queue = resultQueue
            self.__class__._initialized = True
    
    def standby(self) -> None:
        '''Wait to be given a task to execute through the taskQueue.'''
        self.resultQueue.put(QRMessage('Started'))
        # Tells the main process that the child process has successfully started
        while True:
            task: QRTask = self.taskQueue.get()
            task.foo(*task.args, **task.kwargs)
    
    def generateQRCode(self, text, ecLevel) -> None:
        '''
        Generates the qrCodeData that will be painted onto the QR Widget. 
        This function and all the following must execute in a separate process to prevent the GUI from freezing.
        '''
        print('===============')
        print('Text :', text, '\nError Correction Level :', ecLevel)
        start = perf_counter()

        qrCodeData: list[list[str]] = []
        rawData: str = ''

        #### Figure out the appropriate encoding mode ####

        mode: Mode = Mode.NUMERIC
        for char in text:
            newMode: Mode | QRError = Mode.findMode(char)
            if (newMode == QRError.ModeError):
                # There is a character with no available encoding mode.
                self.resultQueue.put(QRResult(success=False, data=char, error=QRError.ModeError))
                return
            elif (newMode.value > mode.value):
                mode = newMode
        rawData += mode.value
        
        print('Mode :', mode)
        
        #### Figure out the appropriate QR Code version ####

        textLength: int = len(text)
        version: int = 1
        foundVersion: bool = False
        while not(foundVersion):
            if (qrdata.getCapacity(version, ecLevel, mode.value) >= textLength):
                foundVersion = True
            else:
                version += 1
        
        print('Version :', version)
        
        #### Create the character count indicator ####

        cciLength: int = qrdata.getCCILength(version, mode.value)
        cci: str = str(bin(textLength))[2:]
        cci = '0' * (cciLength-len(cci)) + cci
        rawData += cci

        print('Character Count Indicator :', cci)

        #### Encode the data using the selected mode ####

        encodedData: str | QRError = Encoder.encode(text, mode)
        if (encodedData == QRError.EncodeError):
            self.resultQueue.put((QRError.EncodeError.value,))
            return
        rawData += encodedData

        print('Encoded Data :', encodedData)

        sleep(100) #fake math
        self.resultQueue.put([0])
        # Temporary, will replace [0] with qrCodeData once this code is finished.

        print(f'Time taken: {perf_counter()-start:.6f} seconds')
    
    @staticmethod
    def resetClass() -> None:
        '''Resets the class attributes to their default values.'''
        __class__._instance = None
        __class__._initialized = False

class Mode(Enum):
    '''Static class used for finding the mode of a given character acording to QR Code mode encoding.'''
    NUMERIC = '0001'
    ALPHANUM = '0010'
    BYTE = '0100'
    KANJI = '1000'

    @staticmethod
    def findMode(char: str) -> Mode | QRError:
        '''
        Returns the mode that will be used to encode the given character, between
        numeric, alphanum, byte, and kanji.
        Returns Mode.ERROR if the character cannot be encoded using any of the four modes.
        '''
        if (Mode.isNumeric(char)):
            return Mode.NUMERIC
        elif (Mode.isAlphanum(char)):
            return Mode.ALPHANUM
        elif (Mode.isByte(char)):
            return Mode.BYTE
        elif (Mode.isKanji(char)):
            return Mode.KANJI
        else:
            return QRError.ModeError
    
    @staticmethod
    def isNumeric(char: str) -> bool:
        '''Returns whether the given character is numeric according to QR Code encoding modes.'''
        return char.isnumeric()
    
    @staticmethod
    def isAlphanum(char: str) -> bool:
        '''Returns whether the given character is alphanumeric according to QR Code encoding modes.'''
        if not(char in Table.ALPHANUM.value):
            return False
        return True

    @staticmethod
    def isByte(char: str) -> bool:
        '''Returns whether the given character is binary/byte according to QR Code encoding modes.'''
        if (ord(char) > 255):
            # print(char + ' n\'est pas byte')
            return False
        return True

    @staticmethod
    def isKanji(char: str) -> bool:
        '''Returns whether the given character is kanji/kana according to QR Code encoding modes.'''
        try:
            b = char.encode('shift_jis')
        except UnicodeEncodeError:
            return False

        if len(b) != 2:
            return False  # Must be a 2-byte Shift-JIS character

        code = int.from_bytes(b, 'big')
        # saves the character's byte value for Kanji encoding later on, 
        # meaning IF AND ONLY IF this function returns True.
        return (0x8140 <= code <= 0x9FFC) or (0xE040 <= code <= 0xEBBF)

class Encoder:
    '''Static class used for encoding a given string using a specific Mode.'''

    @staticmethod
    def encode(text: str, mode: Mode) -> str | QRError:
        '''
        Returns the string corresponding to the given text's 
        encoded value in binary, depending on the given Mode.
        '''
        try:
            if (mode == Mode.NUMERIC):
                return Encoder.encodeNumeric(text)
            elif (mode == Mode.ALPHANUM):
                return Encoder.encodeAlphanum(text)
            elif (mode == Mode.BYTE):
                return Encoder.encodeByte(text)
            else:
                return Encoder.encodeKanji(text)
        except Exception:
            return QRError.EncodeError
    
    @staticmethod
    def encodeNumeric(text: str) -> str:
        '''
        Returns the string corresponding to the given character's 
        encoded value in binary using numeric encoding.
        '''
        result: str = ''
        start: int = 0
        while (start < len(text)):
            currentGroup: int = int(text[start:start+3])
            groupBin: str = str(bin(currentGroup))[2:]
            lenGroup: int = len(str(currentGroup))
            if (lenGroup == 3):
                groupBin = '0'*(10-len(groupBin)) + groupBin
            elif (lenGroup == 2):
                groupBin = '0'*(7-len(groupBin)) + groupBin
            else:
                groupBin = '0'*(4-len(groupBin)) + groupBin
            #print(groupBin)
            result += groupBin
            start += 3
        return result

    
    @staticmethod
    def encodeAlphanum(text: str) -> str:
        '''
        Returns the string corresponding to the given character's 
        encoded value in binary using alphanumeric encoding.
        '''
        result: str = ''
        start: int = 0
        while (start < len(text)):
            currentGroup: str = text[start:start+2]
            charList: list[str] = Table.ALPHANUM.value
            if (len(currentGroup) == 1):
                groupBin: str = str(bin(charList.index(currentGroup)))[2:]
                groupBin = '0'*(6-len(groupBin)) + groupBin
            else:
                groupBin: str = str(bin( 
                    45*charList.index(currentGroup[0]) +  charList.index(currentGroup[1])
                ))[2:]
                groupBin = '0'*(11-len(groupBin)) + groupBin
            result += groupBin
            start += 2
            print(groupBin)
        return result

    
    @staticmethod
    def encodeByte(text: str) -> str:
        '''
        Returns the string corresponding to the given character's 
        encoded value in binary using byte encoding.
        '''
        pass
    
    @staticmethod
    def encodeKanji(text: str) -> str:
        '''
        Returns the string corresponding to the given character's 
        encoded value in binary using kanji encoding.
        '''
        result: str = ''
        for char in text:
            charByte: int = int.from_bytes(char.encode('shift_jis'), 'big')
            if (0x8140 <= charByte <= 0x9FFC):
                newVal: int = charByte - 0x8140
                print(newVal)
            elif (0xE040 <= charByte <= 0XEBBF):
                ...
            else:
                raise ValueError('Text contains an invalid character!')

@dataclass(frozen=True)
class QRMessage:
    '''Message to be sent over a multiprocessing queue during IPC'''
    message: str

@dataclass(frozen=True)
class QRTask:
    '''Tasks to be given to a child process over a multiprocessing queue during IPC'''
    foo: function
    args: tuple = ()
    kwargs: dict = {}

@dataclass(frozen=True)
class QRResult:
    '''Message to be sent over a multiprocessing queue during IPC once a task is finished'''
    success: bool
    data: list | None = None
    error: QRError | None = None

class Table(Enum):
    '''Enum used for storing the lists of characters allowed in a mode, when needed.'''
    ALPHANUM = (
                [str(num) for num in range(10)] + 
                [chr(char) for char in range(ord('A'), ord('Z')+1)] +
                [' ', '$', '%', '*', '+', '-', '.', '/', ':']
    )

class QRError(Enum):
    ModeError = auto()
    
    EncodeError = auto()

if __name__ == '__main__':
    freeze_support()
    program = Program()
    program.execute()