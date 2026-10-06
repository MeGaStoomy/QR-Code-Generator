'''
This file contains all the code related to finding encoding modes and encoding data using specific modes.
'''

from enum import Enum
from qrerrors import QRError
from qrdata import ALPHANUM_CHARS

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
            #raise e
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
            lenGroup: int = len(text[start:start+3])
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