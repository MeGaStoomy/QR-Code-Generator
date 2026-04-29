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
from capacities import getCapacity
from typing_extensions import Self, Any
from time import sleep, time
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

global SCRIPT_DIR
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class Program:
    '''Wrapper class for the window and application instances.'''
    def __init__(self):
        self.app = Application(self)
        self.window = Window(self)
    
    def execute(self) -> None:
        '''Executes the program.'''
        self.window.show()
        self.app.exec()

class Application(QApplication):
    def __init__(self, program: Program):
        super().__init__([])
        self.program: Program = program
        self.text: str | None = None
        self.eccLevel: int | None = None
        self.resultQueue: Queue | None = None
        self.checkTimer: QTimer = QTimer(self)
        self.checkTimer.timeout.connect(self.checkQueue)
        self.qrProcessStart: float | None = None
        self.qrWorker: QRWorker | None = None
        self.qrProcess: Process | None = None

        icon_path = os.path.join(SCRIPT_DIR, "icon.ico")
        self.setWindowIcon(QIcon(icon_path))
    
    def createQRProcess(self) -> None:
        '''Creates and starts a process, in which the QR Code's rawData will be generated.'''
        window: Window = self.program.window
        window.disableQRCodeLayout()
        text = window.textEntry.toPlainText()
        if (text == ''):
            print('Text cannot be empty!')
            window.enableQRCodeLayout()
            return
        self.text = text
        self.eccLevel = window.eccButtonGroup.checkedId()
        self.resultQueue = Queue()
        self.qrWorker = QRWorker(self.text, self.eccLevel, self.resultQueue)
        self.qrProcess = Process(target=self.qrWorker.generateQRCode, daemon=True)
        self.qrProcess.start()
        self.qrProcessStart = time()
        self.checkTimer.start(100)
    
    def checkQueue(self) -> None:
        '''Checks the resultQueue to see whether the QRWorker has sent back something or not.'''
        if not(self.resultQueue is None):
            if (time() - self.qrProcessStart > 10):
                print('Process timed out!')
                self.terminateQRProcess()
            elif not(self.resultQueue.empty()):
                rawData: list | tuple = self.terminateQRProcess(getRawData=True)
                if (type(rawData) == list):
                    # No errors, continue normally.
                    print('No errors occured during generation.')
                elif (type(rawData) == tuple):
                    # An error occured, rawData: tuple[errorCode: int, *args].
                    if (rawData[0] == 0):
                        # Error during encoding of a character, rawData: tuple[0, character that failed]
                        print(chr(rawData[1]) + ' cannot be encoded using any of the four available modes!')
                
    
    def terminateQRProcess(self, getRawData: bool = False) -> None | list | tuple:
        '''
        Properly terminates the QR Process and everything related, 
        and retrieves data from the queue if needed, in which case rawData
        should be a list, or an integer if an error occured during generation.
        '''
        self.checkTimer.stop()
        self.qrProcess.terminate()
        rawData: None | list | tuple = None
        if (getRawData):
            try: 
                rawData = self.resultQueue.get(block=False, timeout=5000)
            except TimeoutError:
                print('Error while retrieving rawData from the Queue!')
        self.resultQueue = None
        self.qrWorker.resetClass()
        self.program.window.enableQRCodeLayout()
        return rawData

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
    
    def maximize(self, event) -> None:
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

    def _setupWindowGeometry(self) -> None:
        '''Creates and sets up the window geometry.'''
        self.windowIsMaximized = False
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

        self.titleBarLayout = QHBoxLayout()
        
        self.workingAreaLayout = QHBoxLayout()
        
        self.userInputLayout = QWidget()
        self.userInputLayout.setLayout(QVBoxLayout())

        self.textEntryLayout = QWidget()
        self.textEntryLayout.setLayout(QVBoxLayout())

        self.eccButtonLayout = QWidget()
        self.eccButtonLayout.setLayout(QVBoxLayout())

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

        self.eccButtonGroupTitle = QLabel("Error Correction Level :")
        
        self.eccLowButton = QPushButton("Level L (Low) : Up to 7% data recovery.")
        self.eccMediumButton = QPushButton("Level M (Medium) : Up to 15% data recovery.")
        self.eccQuartileButton = QPushButton("Level Q (Quartile) : Up to 25% data recovery.")
        self.eccHighButton = QPushButton("Level H (High) : Up to 30% data recovery.")

        self.eccButtonGroup = QButtonGroup()
        self.eccButtonGroup.addButton(self.eccLowButton, 1)
        self.eccButtonGroup.addButton(self.eccMediumButton, 2)
        self.eccButtonGroup.addButton(self.eccQuartileButton, 3)
        self.eccButtonGroup.addButton(self.eccHighButton, 4)
        for button in self.eccButtonGroup.buttons():
            button.setCheckable(True)
        self.eccMediumButton.setChecked(True)

        self.workingAreaLimiter = QWidget()

        self.qrCode = QRWidget()
        self.qrCode.setLayout(QVBoxLayout())

        self.qrCodeText = QLabel("Waiting for input...")

        self.qrCodeLoadingIcon = QLabel()
        
        self.generateButton = QPushButton("Generate")
        self.generateButton.setAutoDefault(False)
        self.generateButton.clicked.connect(self.program.app.createQRProcess)

        self.downloadButton = QPushButton()
        self.downloadButton.setAutoDefault(False)

        self.copyButton = QPushButton()
        self.copyButton.setAutoDefault(False)

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
        userInputLayout.addWidget(self.eccButtonLayout)
        
        textEntryLayout = self.textEntryLayout.layout()
        textEntryLayout.addWidget(self.textEntryTitle)
        textEntryLayout.addWidget(self.textEntry)

        eccButtonLayout = self.eccButtonLayout.layout()
        eccButtonLayout.addWidget(self.eccButtonGroupTitle)

        for button in self.eccButtonGroup.buttons():
            eccButtonLayout.addWidget(button)

        qrCode = self.qrCode.layout()
        qrCode.addWidget(self.qrCodeText)
        qrCode.addWidget(self.qrCodeLoadingIcon)

        qrCodeLayout = self.qrCodeLayout.layout()
        qrCodeLayout.addWidget(self.qrCode)
        qrCodeLayout.addLayout(self.qrCodeButtonsLayout)

        self.qrCodeButtonsLayout.addWidget(self.generateButton)
        self.qrCodeButtonsLayout.addWidget(self.downloadButton)
        self.qrCodeButtonsLayout.addWidget(self.copyButton)
    
    def _stylizeWidgets(self) -> None:
        '''Applies all of the style to all the widgets/layouts'''
        titleBarHeight = self.titleBar.height()

        self.outerLayout.setContentsMargins(0, 0, 0, 0)
        self.outerLayout.setSpacing(0)

        self.titleBarLayout.setContentsMargins(0, 0, 0, 0)
        self.titleBarLayout.setSpacing(0)

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

        eccButtonLayout = self.eccButtonLayout.layout()
        eccButtonLayout.setContentsMargins(20, 0, 20, 40)
        eccButtonLayout.setSpacing(0)

        self.eccButtonGroupTitle.setObjectName("ECCTitle")

        for button in self.eccButtonGroup.buttons():
            button.setObjectName("ECCButton")
        self.eccHighButton.setProperty("position", "last")

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

        icon_path = os.path.join(SCRIPT_DIR, "loading.svg")
        size = int(length/3)
        self.qrCodeLoadingIcon.setPixmap(QPixmap(icon_path).scaled(size,size))
        self.qrCodeLoadingIcon.hide()

        self.qrCodeButtonsLayout.setContentsMargins(0, 20, 0, 0)
        self.qrCodeButtonsLayout.setSpacing(0)
        
        self.generateButton.setFixedSize(length-110, 50)
        self.generateButton.setObjectName("QRButton")

        icon_path = os.path.join(SCRIPT_DIR, "download.svg")
        self.downloadButton.setIcon(QIcon(icon_path))
        self.downloadButton.setIconSize(QSize(32, 32))
        self.downloadButton.setFixedSize(50, 50)
        self.downloadButton.setObjectName("QRButton")
        self.downloadButton.setProperty("style", "small")

        icon_path = os.path.join(SCRIPT_DIR, "copy.svg")
        self.copyButton.setIcon(QIcon(icon_path))
        self.copyButton.setIconSize(QSize(32, 32))
        self.copyButton.setFixedSize(50, 50)
        self.copyButton.setObjectName("QRButton")
        self.copyButton.setProperty("style", "small")

        style_path = os.path.join(SCRIPT_DIR, "style.qss")
        with open(style_path, mode="r", encoding="utf-8") as style:
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
        self.rawData = None

    def paintQRCode(self) -> None:
        '''Paints the QR Code onto the widget, as long as there is rawData to use.'''
        raise NotImplementedError()

class TitleBar(QWidget):
    def __init__(self, parent: Window) -> None:
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
            self.oldClickPos = QCursor.pos()
            self.windowStartPos = self.window().normalPos
    
    def mouseReleaseEvent(self, event) -> None:
        '''Triggered when the title bar is released by the mouse.'''
        if event.button() == Qt.MouseButton.LeftButton:
            self.setMouseTracking(False)
            self.oldClickPos = None
            self.windowStartPos = None
    
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

    def mouseDoubleClickEvent(self, event) -> None:
        '''Triggered when the title bar is double clicked by the mouse.'''
        if event.button() == Qt.MouseButton.LeftButton:
            self.window().maximize(event)

class QRWorker:
    '''Class whose instance is ran in another process to generate the QR Code's rawData.'''
    _instance: None | __class__ = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs) -> Self:
        '''Ensures only one QRWorker can exist at a time.'''
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, text: str, eccLevel: int, resultQueue: Queue) -> None:
        '''Initializes the QRWorker.'''
        if self.__class__._initialized:
            print('Can only create one QRWorker at a time!')
            return
        else:
            self.text: str = text
            self.eccLevel: int = eccLevel
            self.resultQueue: Queue = resultQueue
            self.__class__._initialized = True

    def generateQRCode(self) -> None:
        '''
        Generates the rawData that will be painted onto the QR Widget. 
        This function and all the following must execute in a separate process to prevent the GUI from freezing.
        '''
        rawData: str = ''
        segments: list[tuple[str, str, str]] = []
        currentSegment: list = []
        currentMode: None | int = None
        modeBits: dict[int, str] = {
            1:'0001',
            2:'0010',
            3:'0100',
            4:'1000',
        }

        for char in self.text:
            mode: int = ModeFinder.findMode(char)
            if not(0 < mode < 5):
                # A character has failed to encode, mode is now equal to ord(char)
                self.resultQueue.put((0, mode))
                return
            elif (mode != currentMode):
                if (currentMode):
                    segments.append((modeBits[currentMode],  ''.join(currentSegment)))
                currentMode = mode
                currentSegment = []
        
        #sleep(100) #fake math
        #self.resultQueue.put(self.rawData)
    
    @staticmethod
    def resetClass() -> None:
        '''Resets the class attributes to their default values.'''
        __class__._instance = None
        __class__._initialized = False
            

class ModeFinder:
    '''Static class used for finding the mode of a given string acording to QR Code mode encoding.'''

    @staticmethod
    def findMode(char: str) -> int:
        '''
        Returns the mode that will be used to encode the given character, between
        numeric, alphanum, byte, and kanji.
        Returns  if the character cannot be encoded using any of the four modes.
        '''
        if (ModeFinder.isNumeric(char)):
            return 1
        elif (ModeFinder.isAlphanum(char)):
            return 2
        elif (ModeFinder.isByte(char)):
            return 3
        elif (ModeFinder.isKanji(char)):
            return 4
        else:
            return ord(char)
    
    @staticmethod
    def isNumeric(char: str) -> bool:
        '''Returns whether the given character is numeric according to QR Code encoding modes.'''
        return char.isnumeric()
    
    @staticmethod
    def isAlphanum(char: str) -> bool:
        '''Returns whether the given character is alphanumeric according to QR Code encoding modes.'''
        charList: list[str] = (
                [str(num) for num in range(10)] + 
                [chr(char) for char in range(ord('A'), ord('Z')+1)] +
                [' ', '$', '%', '*', '+', '-', '.', '/', ':']
        )
        if not(char in charList):
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
        return (0x8140 <= code <= 0x9FFC) or (0xE040 <= code <= 0xEAFC)

if __name__ == '__main__':
    freeze_support()
    program = Program()
    program.execute()