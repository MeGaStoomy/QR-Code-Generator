'''
This file contains all the code related directly to the QR Worker and the methods it uses.
'''

from enum import Enum
from time import perf_counter
from typing import Self, Any
from multiprocessing import Queue
from IPC_coms import QRMessage, QRTask, QRResult
from qrdata import ALPHANUM_CHARS, getCapacity, getCCILength, getAlignPosList, ECInfo, getECInfo
from qrerrors import QRError

class QRWorker:
    '''Class whose instance is ran in another process to generate the QR Code's qrCodeData.'''
    _instance: None | Self = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs) -> Self:
        '''Ensures only one QRWorker can exist at a time.'''
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        else:
            print('Can only create one QRWorker at a time!')
        return cls._instance

    def __init__(self, taskQueue: Queue, resultQueue: Queue) -> None:
        '''Initializes the QRWorker.'''
        if not(self.__class__._initialized):
            self.taskQueue: Queue = taskQueue
            self.resultQueue: Queue = resultQueue
            self.__class__._initialized = True
    
    def idle(self) -> None:
        '''Wait to be given a task to execute through the taskQueue.'''
        self.resultQueue.put(QRMessage.ProcessStarted)
        # Tells the main process that the child process has successfully started
        while True:
            task: QRTask = self.taskQueue.get()
            start = perf_counter()
            result: Any = task.foo(*task.args, **task.kwargs)
            print(f'Time taken: {perf_counter()-start:.6f} seconds')
            self.resultQueue.put(result)
    
    @staticmethod
    def generateQRCode(text: str, ecLevel: int) -> QRResult:
        '''
        Generates the qrCodeData that will be painted onto the QR Widget. 
        This function and all the following must execute in a separate process to prevent the GUI from freezing.
        '''
        print('===============')
        print('Text :', text, '\nError Correction Level :', ecLevel)

        qrCodeData: list[list[str]] = []
        rawData: str = ''
        # rawData contains only the encoded information + error correcting codewords.
        # qrCodeData is the serialized version of rawData, containing alignment paterns, timing paterns, etc,
        # in a matrice of strings.   

        #### Figure out the appropriate encoding mode ####

        mode: Mode | QRResult = QRWorker.findEncodingMode(text)
        if (isinstance(mode, QRResult)):
            return mode
        rawData += mode.value
        #rawData += '/'
        
        print('Mode :', mode, mode.value)
        
        #### Figure out the appropriate QR Code version ####

        textLength: int = len(text)
        version: int | QRResult = QRWorker.findQRVersion(textLength, ecLevel, mode)
        if (isinstance(version, QRResult)):
            return version
        
        print('Version :', version)
        
        #### Create the character count indicator ####

        cci: str | QRResult = QRWorker.getCCI(textLength, version, mode)
        rawData += cci
        #rawData += '/'

        print('Character Count Indicator :', cci)

        #### Encode the data using the selected mode ####

        encodedData: str | QRError = Encoder.encode(text, mode)
        if (encodedData == QRError.EncodeError):
            return QRResult(wasSuccessful=False, error=QRError.EncodeError)
        rawData += encodedData
        #rawData += '/'

        print('Encoded Data :', encodedData)
        print('Pre-terminator length :', len(rawData))

        #### Add terminator bits if necessary ####

        ecInfo: ECInfo = getECInfo(version, ecLevel)

        terminator: str = QRWorker.getTerminatorBits(len(rawData), ecInfo)
        rawData += terminator
        #rawData += '/'

        print('Terminator :', terminator)

        #### Add pad bytes if necessary ####

        padBits: str = QRWorker.getOctetFiller(len(rawData))
        rawData += padBits
        #rawData += '/'

        padBytes: str = QRWorker.getPadBytes(len(rawData), ecInfo)
        rawData += padBytes
        #rawData += '/'

        #### Error Correction Codewords creation ####

        print(ecInfo)
        for i in range(0, ecInfo.totalDataCodewords):
            codeword: str = rawData[i*8:i*8+8]
            print(f'(codeword #{i+1}) {rawData[i*8:i*8+8]}')

        #### End ####

        print('Final rawData :', rawData)

        #sleep(100) #fake math
        return QRResult(wasSuccessful=True, data=qrCodeData)

    @staticmethod
    def findEncodingMode(text: str) -> Mode | QRResult:
        '''Returns the encoding mode to be used for encoding a string, or a QRResult if there was an error.'''
        mode: Mode = Mode.NUMERIC
        for char in text:
            newMode: Mode | QRError = Mode.findMode(char)
            if (newMode is QRError.ModeError):
                # There is a character with no available encoding mode.
                return QRResult(wasSuccessful=False, data=char, error=QRError.ModeError)
            elif (newMode.value > mode.value):
                mode = newMode
        return mode
    
    @staticmethod
    def findQRVersion(textLength: int, ecLevel: int, mode: Mode) -> int | QRResult:
        '''
        Returns the QR Code version to be used depending on the given length of the text to encode,
        error correction level, and encoding mode, or a QRResult if there was an error.
        '''
        version: int = 1
        while (version < 41):
            if (getCapacity(version, ecLevel, mode.value) >= textLength):
                return version
            else:
                version += 1
        return QRResult(wasSuccessful=False, error=QRError.VersionError)
    
    @staticmethod
    def getCCI(textLength: int, version: int, mode: Mode) -> str:
        '''
        Returns the character count indicator depending on the given length of the text
        to encode, the QR Code version used, and the encoding mode.
        '''
        cciLength: int = getCCILength(version, mode.value)
        cci: str = str(bin(textLength))[2:]
        cci = '0' * (cciLength-len(cci)) + cci
        return cci
    
    @staticmethod
    def getTerminatorBits(rawDataLength: int, ecInfo: ECInfo) -> str:
        '''
        Returns the terminator bits to be used (if necessary) depending on the given rawData, version,
        and error correction level.
        '''
        codewordQuantity: int = ecInfo.totalDataCodewords
        bitQuantity: int = codewordQuantity*8
        print('Number of data codewords :', codewordQuantity, '\nWhich is :', bitQuantity, 'bits')
        diff: int = bitQuantity - rawDataLength
        terminator: str = '0'*min(4, diff)
        return terminator
    
    @staticmethod
    def getOctetFiller(rawDataLength: int) -> str:
        '''Returns the string of zeros that should be used to make the length of the rawData a multiple of 8.'''
        mod8: int = 8 - rawDataLength%8
        if (mod8 == 8): mod8 = 0
        padBits: str = '0'*mod8
        print('Modulo 8 :', mod8)
        return padBits
    
    @staticmethod
    def getPadBytes(rawDataLength: int, ecInfo: ECInfo) -> str:
        '''
        Returns the string of pad bytes that should be used to fill up the 
        remaining space in the QR Code.
        '''
        PAD_BYTES: tuple[str, str] = ('11101100', '00010001')
        padBytes: str = ''
        bitQuantity: int = ecInfo.totalDataCodewords*8
        missingBytes: float = (bitQuantity-rawDataLength) / 8
        print('Missing bytes :', missingBytes)
        addedBytes: str = ''
        for i in range(int(missingBytes)):
            padBytes += PAD_BYTES[i%2]
            addedBytes += PAD_BYTES[i%2] + '/'
        print('Added bytes :', addedBytes[:-1])
        return padBytes
    
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
    U8 = 'USE Mode.BYTE.value'

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
        elif (Mode.isU8(char)):
            return Mode.U8
        else:
            return QRError.ModeError
    
    @staticmethod
    def isNumeric(char: str) -> bool:
        '''Returns whether the given character is numeric according to QR Code encoding modes.'''
        return char.isnumeric()
    
    @staticmethod
    def isAlphanum(char: str) -> bool:
        '''Returns whether the given character is alphanumeric according to QR Code encoding modes.'''
        if not(char in ALPHANUM_CHARS):
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

    @staticmethod
    def isU8(char: str) -> bool:
        '''Returns whether the given character is UTF-8 according to QR Code encoding modes.'''
        pass

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
            elif (mode == Mode.U8):
                return Encoder.encodeU8(text)
            else:
                return Encoder.encodeKanji(text)
        except Exception as e:
            raise e
            # temporary, will replace for the return later when debugging and coding is done.
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
            charList: list[str] = ALPHANUM_CHARS
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
            #print(groupBin)
        return result

    
    @staticmethod
    def encodeByte(text: str) -> str:
        '''
        Returns the string corresponding to the given character's 
        encoded value in binary using byte encoding.
        '''
        result: str = ''
        for char in text:
            charBin: str = str(bin(ord(char)))[2:]
            charBin = '0'*(8-len(charBin)) + charBin
            result += charBin
        return result
    
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
                charHex: str = hex(charByte - 0x8140)[2:]
            elif (0xE040 <= charByte <= 0XEBBF):
                charHex: str = hex(charByte - 0xC140)[2:]
            else:
                raise ValueError('Text contains non-kanji character!')
            charHex = '0'*(4-len(charHex)) + charHex
            bigByte: int = int('0x' + charHex[0:2], 16)
            tinyByte: int = int('0x' + charHex[2:4], 16)
            encodedChar: int = bigByte*0xC0 + tinyByte
            encodedBin: str = str(bin(encodedChar))[2:]
            encodedBin = '0'*(13-len(encodedBin)) + encodedBin
            result += encodedBin
        return result

    @staticmethod
    def encodeU8(text: str) -> str:
        '''
        Returns the string corresponding to the given character's 
        encoded value in binary using UTF-8 encoding.
        '''
        pass