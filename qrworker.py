'''
This file contains all the code related directly to the QR Worker (AKA the QR Code generator) and the methods it uses.
'''

from time import perf_counter, sleep
from typing import Self, Any
from multiprocessing import Queue
from IPC_coms import QRMessage, QRTask, QRResult
from qrerrors import QRError
from reed_solomon import ReedSolomon
from modules import Module
from encoder import Mode, Encoder
from masker import Masker
from qrdata import (
    getCapacity, 
    getCCILength, 
    ECInfo, 
    getECInfo, 
    getRemainderBits,
    getQRCodeDimensions,
)

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
        while True:
            task: QRTask = self.taskQueue.get()
            print('starting task')
            start = perf_counter()
            result: Any = task.foo(*task.args, **task.kwargs)
            print(f'Time taken: {perf_counter()-start:.6f} seconds')
            self.resultQueue.put(result)
    
    @staticmethod
    def generateQRCode(text: str, ecLevel: int) -> QRResult:
        '''
        Generates the qrCodeData that will be painted onto the QR Widget. 
        This function and all the following must execute in a separate process to prevent the application GUI from freezing during execution.
        '''
        print('===============')
        print('Text :', text, '\nError Correction Level :', ecLevel)

        qrCodeData: list[list] = []
        rawData: str = ''
        # rawData contains only the encoded information + error correcting codewords.
        # qrCodeData is the serialized version of rawData, containing alignment paterns, timing paterns, etc,
        # in a list of strings.   

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

        ecBlocks: list[list[int]] = []
        dataBlocks: list[str] = []
        ecBlocks, dataBlocks = ReedSolomon.getECCodewords(rawData, ecInfo)

        #### Interleaving process ####

        cutDataBlocks: list[list[str]] = [QRWorker.cutBitString(block) for block in dataBlocks]
        cutECBlocks: list[list[str]] = [[bin(codeword)[2:] for codeword in block] for block in ecBlocks]
        QRWorker.addZeros(cutECBlocks)
        print(sum([len(block) for block in cutDataBlocks]))
        print(sum([len(block) for block in cutECBlocks]))
        rawData: str = QRWorker.interleaveCodewords(cutDataBlocks) + QRWorker.interleaveCodewords(cutECBlocks)
        print(len(rawData))

        #### Add remainder bits if necessary ####
        
        rawData += getRemainderBits(version)

        #### Create empty matrix ####

        dimensions: int = getQRCodeDimensions(version)
        qrCodeData = [[None for _ in range(dimensions)] for _ in range(dimensions)]

        #### Add finder patterns ####

        Module.addFinderPatterns(qrCodeData)

        #### Add separators ####

        Module.addSeparators(qrCodeData)

        #### Add alignment patterns ####

        Module.addAlignmentPattern(qrCodeData, version)

        #### Add timing patterns ####

        Module.addTimingPatterns(qrCodeData)

        #### Add the reserved areas ####

        Module.addReservedAreas(qrCodeData, version)

        #### Put rawData into qrCodeData ####

        data: list[str] = [bit for bit in rawData]
        Module.placeData(data, qrCodeData)

        #### Find the best mask and apply it ####

        qrCodeData, maskUsed = Masker.applyBestMask(qrCodeData)
        exportQRCodeAsTextFile(qrCodeData, name='qr_code_test')

        #### Add the 15-bit format string (and 18-bit version string if needed) ####

        Module.placeFormatInformation(qrCodeData, ecLevel, maskUsed)
        if version >= 7:
            Module.placeVersionInformation(qrCodeData, version)

        #### Remove Module.ReservedModule instances.

        Module.removeReservedModules(qrCodeData)
        
        #### End ####

        #sleep(100) #fake math
        exportQRCodeAsTextFile(qrCodeData)
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
    def cutBitString(bitString: str) -> list[str]:
        '''Cuts the given bit string and returns it as a list of 8-bit bytes.'''
        byteList: list[str] = []
        for i in range(len(bitString)//8):
            byteStart: int = i*8
            byteEnd: int = i*8+8
            byteList.append(bitString[byteStart:byteEnd])
        return byteList

    @staticmethod
    def addZeros(blockList: list[list[str]]) -> None:
        '''Adds zeros to each binary codeword to turn them all into 8-bit bytes.'''
        for block in blockList:
            print(f"Before : {block}")
            for i in range(len(block)):
                block[i] = '0'*(8-len(block[i])) + block[i]
            print(f"After : {block}")

    @staticmethod
    def interleaveCodewords(blockList: list[list]) -> str:
        '''Interleaves the codewords into a string.'''
        interleavedCodewords: str = ''
        while any(blockList):
            for block in blockList:
                try: 
                    interleavedCodewords += block.pop(0)
                except IndexError: 
                    continue
                except Exception as e:
                    raise e
        return interleavedCodewords

    @staticmethod
    def resetClass() -> None:
        '''Resets the class attributes to their default values.'''
        __class__._instance = None
        __class__._initialized = False



def exportQRCodeAsTextFileOld(qrCodeData: list[list], name: str = 'qr_code') -> None:
    '''Temporary test function that takes in the qr code matrix and writes its contents to a text file in the local directory to visualize it.'''
    import sys, os
    if getattr(sys, 'frozen', False):
        # running as a compiled binary
        SCRIPT_DIR: str = os.path.dirname(sys.executable)
    else:
        # running as normal python
        SCRIPT_DIR: str = os.path.dirname(os.path.abspath(__file__))
    with open(SCRIPT_DIR + f'\\{name}.txt', 'w') as file:
        for row in qrCodeData:
            fileLine: str = ''
            for module in row:
                if module == None:
                    fileLine += 'N '
                elif isinstance(module, Module.ReservedModule):
                    #print('Module still left!')
                    fileLine += module.value + ' '
                else:
                    fileLine += module + ' '
            file.write(fileLine + '\n')

def exportQRCodeAsTextFile(qrCodeData: list[list], name: str = 'qr_code') -> None:
    '''Temporary test function that takes in the qr code matrix and writes its contents to a text file in the local directory to visualize it.'''
    import sys, os
    if getattr(sys, 'frozen', False):
        # running as a compiled binary
        SCRIPT_DIR: str = os.path.dirname(sys.executable)
    else:
        # running as normal python
        SCRIPT_DIR: str = os.path.dirname(os.path.abspath(__file__))
    with open(SCRIPT_DIR + f'\\{name}.txt', 'w', encoding='UTF-8') as file:
        for row in qrCodeData:
            fileLine: str = ''
            for module in row:
                if module == None:
                    fileLine += 'N '
                elif isinstance(module, Module.ReservedModule):
                    #print('Module still left!')
                    fileLine += module.value + ' '
                else:
                    fileLine += module + ' '
            file.write(fileLine + '\n')

dimensions: int = 25
#exportQRCodeAsTextFile([[None for _ in range(dimensions)] for _ in range(dimensions)])