'''
This file contains code related to the creation of Reed-Solomon error correcting codewords.
'''

from typing import NamedTuple, override

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
    for i in range(10, 256):
        i = str(i)
        exp: str = ''
        for num in i: exp += EXPONENT_CHARS[num]
        EXPONENT_CHARS[i] = exp
    ALPHA_CHAR: str = 'α'

    def __init__(self, terms: list[list]):
        '''Initiates the polynomial.'''
        self.terms: list[list] = terms if terms else []
        # each tuple corresponds to a term within the polynomial, so α^34*x^48 is [[34, 48]].
        # make sure to enter the EXPONENTS.

    def __str__(self):
        string: str = ""
        for term in self.terms:
            string += self.ALPHA_CHAR + self.EXPONENT_CHARS[str(term[0])] + 'x' + self.EXPONENT_CHARS[str(term[1])] + ' + '
        return string[:-3]

    def __repr__(self):
        return f'<Polynomial {self.__str__()}>'

    def __mul__(self, other: Polynomial) -> Polynomial:
        pol: list[list] = []
        for termA in self.terms:
            for termB in other.terms:
                alphaExp: int = GaloisField.valToExp(GaloisField.mul(GaloisField.expToVal(termA[0]), GaloisField.expToVal(termB[0])))
                xExp: int = GaloisField.valToExp(GaloisField.mul(GaloisField.expToVal(termA[1]), GaloisField.expToVal(termB[1])))
                termC: list = [alphaExp, xExp]
                pol.append(termC)
        result: Polynomial = Polynomial(pol)
        result.combineLikeTerms()
        return result

    def combineLikeTerms(self) -> None:
        '''Combines like terms within the polynomial.'''
        newTerms: dict[int, int] = {}
        for term in self.terms:
            newTerms[term[1]] = newTerms.get(term[1], 0) ^ GaloisField.expToVal(term[0])
        self.terms = [[GaloisField.valToExp(v), k] for k, v in newTerms.items()]
                    
    @staticmethod
    def getGenerator(n: int) -> Polynomial:
        '''Returns the generator polynomial for n EC Codewords.'''
        if n == 1:
            return Polynomial([[0, 1], [0, 0]])
        else:
            return Polynomial.getGenerator(n-1) * Polynomial([[0, 1], [n-1, 0]])
 
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
        xExp: int = GaloisField.valToExp(x)
        yExp: int = GaloisField.valToExp(y)
        newExp: int = xExp+yExp
        if (newExp >= 256): newExp %= 255
        return GaloisField.expToVal(newExp)
    
    @staticmethod
    def expToVal(n: int) -> int:
        '''Returns the value of α^n inside GF(256).'''
        return GaloisField.GALOIS_VALS[n]
    
    @staticmethod
    def valToExp(val: int) -> int:
        '''Returns the integer n for which α^n = val inside GF(256).'''
        return GaloisField.GALOIS_VALS.index(val)