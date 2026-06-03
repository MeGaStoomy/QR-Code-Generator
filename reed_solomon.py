'''
This file contains code related to the creation of Reed-Solomon error correcting codewords.
'''

from typing import NamedTuple

class ReedSolomon:
    '''Static class used for any method related to error correction.'''

    @staticmethod
    def foo():
        pass

class Polynomial:
    '''Class used for representing polynomials in GF(256).'''
    EXPONENT_CHARS: dict[str, str] = {
        '0': chr(0x2070),
        '1': chr(0x00B9),
        '2': chr(0x00B2),
        '3': chr(0x00B3),
    }
    for i in range(0x2074, 0x207A):
        EXPONENT_CHARS[str(i-0x2070)] = chr(i)
    ALPHA_CHAR: str = 'α'
    GENERATOR_POLS: list[Polynomial] = []
    # will get generated inside qrworker.

    def __init__(self, terms: list[int] | None = None) -> None:
        self.terms: list[int] = terms if terms else []
        # self.terms is the list of integers where the ints represent each term's coefficient inside GF(256)
        # for exemple, 35x^4+25x^3+98x^1 would be []
            
    def __repr__(self) -> str:
        return f'<Polynomial {self.__str__()}>'

    def __str__(self) -> str:
        n: int = len(self)
        if (n == 0):
            return '0'
        else:
            strResult: str = ''
            for i in range(n-1):
                if (self[i] != 0):
                    strTerm: str = f'{'+' if self[i] > 0 else ''}'
                    strTerm += str(self[i]) + 'x' + Polynomial._getStrExp(n-i-1)
                    strResult += strTerm
            strResult += f'+{Polynomial.ALPHA_CHAR + self._getStrExp(self[-1])}'
            return strResult
    
    def __getitem__(self, pos):
        return self.terms[pos]
    
    def __len__(self):
        return len(self.terms)

    def __truediv__(self, divisor: Polynomial) -> Polynomial:
        '''Returns the result of the Polynomial Long Division of self with other.'''
        if not(isinstance(divisor, Polynomial)):
            return NotImplemented
        resPol: Polynomial = Polynomial()
        
        return resPol
    
    @staticmethod
    def _getStrExp(exp: int) -> str:
        '''
        Helper method that, given an integer, returns its string value using the exponent characters
        defined in Polynomial.EXPONENT_CHARS

        Polynomial._getStrExp(2936246) -> '²⁹³⁶²⁴⁶'
        '''
        strExp: str = ''
        for num in str(exp):
            strExp += Polynomial.EXPONENT_CHARS[num]
        return strExp  

class GaloisField:
    '''Static class used for arithmetic operations inside GF(256)'''
    GALOIS_VALS: list[int] = [1]
    for n in range(1, 256):
        val: int = GALOIS_VALS[n-1] * 2
        if (val >= 256):
            val ^= 285
        GALOIS_VALS.append(val)

    @staticmethod
    def add(x: int, y: int) -> int:
        '''Returns the sum of x and y, done inside GF(256).'''
        return abs(x) ^ abs(y)
    
    @staticmethod
    def mul(x: int, y: int) -> int:
        '''Returns the product of x and y, done inside GF(256).'''
        xExp: int = GaloisField.GALOIS_VALS.index(x)
        yExp: int = GaloisField.GALOIS_VALS.index(y)
        newExp: int = xExp+yExp
        if (newExp >= 256): newExp %= 255
        return GaloisField.GALOIS_VALS[newExp]
    
    @staticmethod
    def alphaToVal(n: int) -> int:
        '''Returns the value of α^n inside GF(256).'''
        return GaloisField.GALOIS_VALS[n]
    
    @staticmethod
    def valToAlpha(val: int) -> int:
        '''Returns the integer n for which α^n = val inside GF(256).'''
        return GaloisField.GALOIS_VALS.index(val)