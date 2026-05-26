'''
This file contains code related to the creation of Reed-Solomon error correcting codewords.
'''

class ReedSolomon:
    '''Static class used for any method related to error correction.'''

    @staticmethod
    def foo():
        pass

class Polynomial:
    '''Class used for representing polynomials in a Galois Field'''
    EXPONENT_CHARS: dict[str, int] = {
        '0': 0x2070,
        '1': 0x00B9,
        '2': 0x00B2,
        '3': 0x00B3,
    }
    for i in range(0x2074, 0x207A):
        EXPONENT_CHARS[str(i-0x2070)] = i

    def __init__(self, terms: dict | None = None) -> None:
        '''Initializes the polynomial.'''
        self.terms: dict[str, int] = terms if terms else {}
        self.sortKeys()
        # self.terms is in the form {e: c, e: c, ...}
        # where n is the exponent and c the coefficient
        # 3x⁴ would be 4: 3
    
    def __add__(self, other: Polynomial) -> Polynomial:
        '''Dunder method for addition'''
        new: Polynomial = Polynomial()
        for poly in [self, other]:
            for key in poly.terms.keys():
                if not(key in new.terms.keys()):
                    res: int = self.terms.get(key, 0) + other.terms.get(key, 0)
                    if (res != 0):
                        new.terms[key] = res
        new.sortKeys()
        return new
    
    def __sub__(self, other: Polynomial) -> Polynomial:
        '''Dunder method for substraction'''
        negated: Polynomial = Polynomial({k: -v for k, v in other.terms.items()})
        return self + negated
    
    def __mul__(self) -> Polynomial:
        '''Dunder method for multiplication'''
        ...

    def __repr__(self) -> str:
        '''Returns the representation of the polynomial.'''
        return f'<Polynomial {str(self)}>'

    def __str__(self) -> str:
        '''Returns the string representation of the polynomial.'''
        res: str = ''
        for key, coef in self.terms.items():
            if (coef > 0):
                coef = '+' + str(coef)
            else:
                coef = str(coef)
            if (key == '0'):
                res += coef
            elif (key == '1'):
                res += coef + 'x'
            else:
                exp: str = ''
                for char in key:
                    exp += chr(Polynomial.EXPONENT_CHARS[char])
                res += coef + 'x' + exp
        return res
    
    def sortKeys(self) -> None:
        '''Sorts the keys in self.terms'''
        if (self.terms != {}):
            listKeys: list = list(self.terms.keys())
            listKeys.sort(key=lambda el: int(el), reverse=True)
            for key in listKeys:
                val: int = self.terms[key]
                del self.terms[key]
                self.terms[key] = val

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
        '''Returns the sum of x and y, done in a Galois Field.'''
        return x ^ y
    
    @staticmethod
    def mul(x: int, y: int) -> int:
        '''Returns the product of x and y, done in a Galois Field.'''
        xExp: int = GaloisField.GALOIS_VALS.index(x)
        yExp: int = GaloisField.GALOIS_VALS.index(y)
        newExp: int = xExp+yExp
        if (newExp >= 256): newExp %= 255
        print(f'xExp : {xExp}\nyExp : {yExp}\nnewExp : {newExp}')
        return GaloisField.GALOIS_VALS[newExp]