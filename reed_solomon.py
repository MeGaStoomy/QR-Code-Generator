'''
This file contains code related to the creation of Reed-Solomon error correcting codewords.
'''

from qrdata import ECInfo

class ReedSolomon:
    '''Static class used for any method related to error correction.'''

    @staticmethod
    def getECCodewords(rawData: str, ecInfo: ECInfo) -> tuple[list[list[int]], list[str]]:
        '''
        Returns the Error Correction Codewords for the given generated rawData and ecInfo.
        Additionally, this method also returns the the properly separated data blocks taken from rawData.
        '''
        print(ecInfo)
        dataBlocks: list[str] = ReedSolomon._extractDataBlocks(rawData, ecInfo)  
        ecBlocks: list[list[int]] = [ReedSolomon._getECCodewordsFromBlock(block, ecInfo) for block in dataBlocks]
        return (ecBlocks, dataBlocks)

    @staticmethod
    def getMessagePolynomial(rawData: str) -> Polynomial:
        '''Returns the message polynomial corresponding to the given rawData.'''
        terms: list[list] = []
        print('Block :', rawData)
        codewordList: list[int] = []
        for i in range(len(rawData)//8):
            codeword: str = rawData[i*8:i*8+8]
            codewordList.append(int(codeword, 2))
            print(f'(codeword #{i+1}) {codeword} ({int(codeword, 2)})')
            if not codeword == '00000000':
                terms.append([GaloisField.valToExp(int(codeword, 2)), len(rawData)//8-i-1])
        print(codewordList)
        return Polynomial(terms)

    @staticmethod
    def getGeneratorPolynomial(n: int) -> Polynomial:
        '''Returns the generator polynomial for n EC Codewords.'''
        if n == 1:
            return Polynomial([[0, 1], [0, 0]])
        else:
            return ReedSolomon.getGeneratorPolynomial(n-1) * Polynomial([[0, 1], [n-1, 0]])

    @staticmethod
    def _extractDataBlocks(bitString: str, ecInfo: ECInfo) -> list[str]:
        '''Helper method that extracts the different data blocks from the given bit string.'''
        dataBlocks: list[str] = []
        blockEnd: int = 0
        for i in range(ecInfo.g1Blocks):
            blockStart: int = i*8*ecInfo.g1CodewordsEach
            blockEnd: int = (i+1)*8*ecInfo.g1CodewordsEach
            dataBlocks.append(bitString[blockStart:blockEnd])
            print(f"{blockStart} to {blockEnd}")
        groupTwoStart: int = blockEnd
        for i in range(ecInfo.g2Blocks):
            blockStart: int = i*8*ecInfo.g2CodewordsEach+groupTwoStart
            blockEnd: int = (i+1)*8*ecInfo.g2CodewordsEach+groupTwoStart
            dataBlocks.append(bitString[blockStart:blockEnd])
            print(f"{blockStart} to {blockEnd}")
        return dataBlocks

    @staticmethod
    def _getECCodewordsFromBlock(block: str, ecInfo: ECInfo) -> list[int]:
        '''Helper method that returns the error correction codewords for a specific block of data codewords.'''
        messagePol: Polynomial = ReedSolomon.getMessagePolynomial(block)
        generatorPol: Polynomial = ReedSolomon.getGeneratorPolynomial(ecInfo.ecCodewordsPerBlock)
        print(messagePol.terms)
        print("Message polynomial :", messagePol)
        print("Generator polynomial :", generatorPol)
        for term in messagePol.terms:
            term[1] += ecInfo.ecCodewordsPerBlock
        diff: int = messagePol.terms[0][1] - generatorPol.terms[0][1]
        for term in generatorPol.terms:
            term[1] += diff
        #print("\nFixed message polynomial :", messagePol, "\nAKA :", messagePol.__str__(alphaNotation=False))
        #print("Fixed generator polynomial :", generatorPol, "\nAKA :", generatorPol.__str__(alphaNotation=False))
        ecPolynomial: Polynomial = Polynomial.longDivide(messagePol, generatorPol, len(messagePol.terms))
        ecCodewords: list[int] = [GaloisField.expToVal(term[0]) for term in ecPolynomial.terms]
        print(ecCodewords)
        return ecCodewords

    
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
    for i in range(10, 257):
        i = str(i)
        exp: str = ''
        for num in i: exp += EXPONENT_CHARS[num]
        EXPONENT_CHARS[i] = exp
    ALPHA_CHAR: str = 'α'

    def __init__(self, terms: list[list]):
        '''Initializes the polynomial.'''
        self.terms: list[list[int]] = terms if terms else []
        # each tuple corresponds to a term within the polynomial, so α^34*x^48 is [[34, 48]].
        # make sure to enter the EXPONENTS.

    def __str__(self, alphaNotation: bool = True):
        string: str = ""
        if alphaNotation:
            for term in self.terms:
                string += self.ALPHA_CHAR + self.EXPONENT_CHARS[str(term[0])] + 'x' + self.EXPONENT_CHARS[str(term[1])] + ' + '
        else:
            for term in self.terms:
                string += str(GaloisField.expToVal(term[0])) + 'x' + self.EXPONENT_CHARS[str(term[1])] + ' + '
        return string[:-3]

    def __repr__(self):
        return f'<Polynomial {self.__str__()}>'

    def __mul__(self, other: Polynomial) -> Polynomial:
        '''Returns the Polynomial resulting from the multiplication of the two given Polynomials (self and other)'''
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

    @staticmethod
    def longDivide(message: Polynomial, generator: Polynomial, n: int) -> Polynomial:
        '''Returns the Polynomial resulting from the long division of message Polynomial and the generator Polynomial.'''
        messagePol: Polynomial = Polynomial(message.terms)
        generatorPol: Polynomial = Polynomial(generator.terms)
        for i in range(n):
            if messagePol.terms[0][0] == 256:
                messagePol.terms.pop(0)
                print(f'\nSkipped step {i+1} (lead term was 0)')
            else:
                newPol = generatorPol * Polynomial([[messagePol.terms[0][0], 0]])
                newPol.convertExpToVal()
                messagePol.convertExpToVal()
                newMessageTerms: dict[int, int] = {}
                for term in messagePol.terms:
                    newMessageTerms[term[1]] = term[0]
                for term in newPol.terms:
                    newMessageTerms[term[1]] = GaloisField.add(newMessageTerms.get(term[1], 0), term[0])
                messagePol.terms = [[v,k] for k, v in newMessageTerms.items()]
                messagePol.sort()
                #messagePol.terms = [term for term in messagePol.terms if term[0] != 0]
                messagePol.terms.pop(0)
                messagePol.convertValToExp()
                newPol.convertValToExp()
                #print(f'\nGenerated polynomial (Step {i+1}) :', newPol, "\nAKA :", newPol.__str__(alphaNotation=False))
                #print(f'Message polynomial (Step {i+1}) :', messagePol, "\nAKA :", messagePol.__str__(alphaNotation=False))
            for term in generatorPol.terms:
                term[1] -= 1
        return messagePol

    def combineLikeTerms(self) -> None:
        '''Combines like terms within the polynomial.'''
        newTerms: dict[int, int] = {}
        for term in self.terms:
            newTerms[term[1]] = newTerms.get(term[1], 0) ^ GaloisField.expToVal(term[0])
        self.terms = [[GaloisField.valToExp(v), k] for k, v in newTerms.items()]

    def convertExpToVal(self) -> None:
        '''Converts the alpha notation to their actual value'''
        for term in self.terms:
            term[0] = GaloisField.expToVal(term[0])

    def convertValToExp(self) -> None:
        '''Converts the actual values (term[0]) to alpha notation.'''
        for term in self.terms:
            term[0] = GaloisField.valToExp(term[0])

    def sort(self) -> None:
        '''Sorts the terms in the Polynomial from highest degree to lowest.'''
        self.terms = sorted(self.terms, key=(lambda term:term[1]), reverse=True)
 
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
        return 0 if n == 256 else GaloisField.GALOIS_VALS[n]
    
    @staticmethod
    def valToExp(val: int) -> int:
        '''Returns the integer n for which α^n = val inside GF(256).'''
        return 256 if val == 0 else GaloisField.GALOIS_VALS.index(val)