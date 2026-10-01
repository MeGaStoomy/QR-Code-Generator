from reed_solomon import Polynomial, ReedSolomon, GaloisField
from qrdata import getECInfo, ECInfo
from time import time
from masker import Masker
from qrworker import exportQRCodeAsTextFile

if __name__ == '__main__':
    testPolynomialMultiplication: bool = False
    testPolynomialAlphaConvertion: bool = False
    testGeneratorPolynomials: bool = False
    testPolynomialSort: bool = False
    testGaloisExpToVal: bool = False
    testGaloisValToExp: bool = False
    testGaloisMul: bool = False
    testDataBlockExtraction: bool = False
    testMaskFunctions: bool = False
    testMaskLineEval: bool = False
    testMaskSquareEval: bool = False
    testMaskPatternEval: bool = True
    if (testPolynomialMultiplication):
        pol1 = Polynomial([[0, 1], [0, 0]])
        pol2 = Polynomial([[0, 1], [1, 0]])
        print(pol1)
        print(pol2)
        pol3: Polynomial = pol1 * pol2
        print(pol3)
        pol4 = Polynomial([[0, 1], [2, 0]])
        print(pol4)
        pol5: Polynomial = pol3 * pol4
        print(pol5)
    if (testGeneratorPolynomials):
        print(ReedSolomon.getGeneratorPolynomial(3))
        print(ReedSolomon.getGeneratorPolynomial(7))
        print(ReedSolomon.getGeneratorPolynomial(8))
        print(ReedSolomon.getGeneratorPolynomial(9))
        print(ReedSolomon.getGeneratorPolynomial(10))
        print(ReedSolomon.getGeneratorPolynomial(34))
        print(ReedSolomon.getGeneratorPolynomial(125))
        print(ReedSolomon.getGeneratorPolynomial(10))
    if (testPolynomialAlphaConvertion):
        pol1: Polynomial = Polynomial([[6,7], [8,1], [4,3], [2,4]])
        print(pol1)
        pol1.convertExpToVal()
        print(pol1)
        pol1.convertValToExp()
        print(pol1)
        pol2: Polynomial = Polynomial([[4,6], [2,7]], alphaNotation=False)
        print(pol2)
        pol3: Polynomial = pol1 * pol2
        print(pol1)
        print(pol2)
        print(pol3)
    if (testPolynomialSort):
        pol: Polynomial = Polynomial([[1,6], [24,5], [4,12], [3,2], [9,4]])
        print("Before sort :", pol)
        pol.sort()
        print("After sort :", pol)
    if (testGaloisExpToVal):
        assert GaloisField.expToVal(0) == 1
        assert GaloisField.expToVal(1) == 2
        assert GaloisField.expToVal(2) == 4
        assert GaloisField.expToVal(7) == 128
        assert GaloisField.expToVal(8) == 29
        assert GaloisField.expToVal(9) == 58
        assert GaloisField.expToVal(10) == 116
        assert GaloisField.expToVal(11) == 232
        assert GaloisField.expToVal(12) == 205
        assert GaloisField.expToVal(71) == 188
    if (testGaloisValToExp):
        assert GaloisField.valToExp(1) == 0
        assert GaloisField.valToExp(2) == 1
        assert GaloisField.valToExp(4) == 2
        assert GaloisField.valToExp(128) == 7
        assert GaloisField.valToExp(29) == 8
        assert GaloisField.valToExp(58) == 9
        assert GaloisField.valToExp(116) == 10
        assert GaloisField.valToExp(232) == 11
        assert GaloisField.valToExp(205) == 12
        assert GaloisField.valToExp(188) == 71
    if (testGaloisMul):
        assert GaloisField.mul(GaloisField.expToVal(2), GaloisField.expToVal(8)) == GaloisField.expToVal(10)
        assert GaloisField.mul(GaloisField.expToVal(200), GaloisField.expToVal(55)) == GaloisField.expToVal(255)
        assert GaloisField.mul(GaloisField.expToVal(201), GaloisField.expToVal(55)) == GaloisField.expToVal(1)
        assert GaloisField.mul(GaloisField.expToVal(0), GaloisField.expToVal(1)) == GaloisField.expToVal(1)
        assert GaloisField.mul(GaloisField.expToVal(170), GaloisField.expToVal(164)) == GaloisField.expToVal(79)
        assert GaloisField.mul(GaloisField.expToVal(255), GaloisField.expToVal(255)) == GaloisField.expToVal(255)
        assert GaloisField.mul(GaloisField.expToVal(0), GaloisField.expToVal(0)) == GaloisField.expToVal(0)
    if (testDataBlockExtraction):
        dataCodewords: list[int] = [67,85,70,134,87,38,85,194,119,50,6,18,6,103,38,
                                    246,246,66,7,118,134,242,7,38,86,22,198,199,146,6,
                                    182,230,247,119,50,7,118,134,87,38,82,6,134,151,50,7,
                                    70,247,118,86,194,6,151,50,224,236,17,236,17,236,17,236]
        ecInfo: ECInfo = getECInfo(5, 3)
        string = ''
        for codeword in dataCodewords:
            binary = bin(codeword)[2:]
            binary = '0'*(8-len(binary)) + binary
            string += binary
        for i in range(len(string)//8):
            print(f"(codeword #{i+1}) {string[i*8:i*8+8]}")
        dataBlocks: list[str] = ReedSolomon._extractDataBlocks(string, ecInfo)
        print(ecInfo)
        print(string)
        print(dataBlocks)
        ecCodewords: list[list[int]] = [ReedSolomon._getECCodewordsFromBlock(block, ecInfo) for block in dataBlocks]
        print(ecCodewords)
    if (testMaskFunctions):
        start = time()
        size: int = 177
        exportQRCodeAsTextFile([['0' for _ in range(size)] for _ in range(size)], 'qr_code_mask_original')
        for i in range(8):
            matrix: list[list] = [['0' for _ in range(size)] for _ in range(size)]
            Masker.applyMask(i, matrix)
            exportQRCodeAsTextFile(matrix, f'qr_code_mask_{i}')
        print(f"Time taken : {time()-start:.6f} seconds.")
    if (testMaskLineEval):
        start: float = time()
        size: int = 21
        matrix: list[list] = [['0' for _ in range(size)] for _ in range(size)]
        matrix = Masker.applyMask(1, matrix)
        print(Masker._evaluateRepeatingLines(matrix))
        print(f"Time taken : {time()-start:.6f} seconds.")
        exportQRCodeAsTextFile(matrix, name='qr_code_test_line')
    if (testMaskSquareEval):
        matrix: list[list] = [['0', '1', '0', '0', '0', '1'],
                              ['0', '0', '1', '0', '0', '0'],
                              ['0', '0', '1', '0', '0', '0'],
                              ['0', '1', '1', '0', '1', '0'],
                              ['0', '1', '1', '0', '0', '0'],
                              ['1', '0', '0', '0', '0', '0']]
        start: float = time()
        print(Masker._evaluateSquares(matrix))
        print(f"Time taken : {time()-start:.6f} seconds.")
        exportQRCodeAsTextFile(matrix, name='qr_code_test_square')
    if (testMaskPatternEval):
        matrix: list[list] = [['0', '0', '0', '0', '1', '0', '1', '1', '1', '0', '1', '0', '0'],
                              ['0', '0', '0', '0', '1', '0', '1', '1', '1', '0', '1', '0', '0'],
                              ['0', '0', '1', '0', '1', '1', '1', '0', '1', '0', '1', '0', '0'],
                              ['0', '0', '0', '0', '1', '0', '1', '1', '1', '0', '1', '0', '0'],
                              ['0', '0', '0', '0', '1', '0', '1', '1', '1', '0', '1', '0', '0'],
                              ['0', '0', '0', '0', '1', '0', '1', '1', '1', '0', '1', '0', '0'],
                              ['0', '0', '0', '0', '1', '0', '1', '1', '1', '0', '1', '0', '0'],
                              ['0', '0', '1', '0', '1', '1', '1', '0', '1', '0', '0', '0', '0'],
                              ['0', '0', '0', '0', '1', '0', '1', '1', '1', '0', '1', '0', '0'],
                              ['0', '0', '0', '0', '1', '0', '1', '1', '1', '0', '1', '0', '0'],
                              ['0', '0', '0', '0', '1', '0', '1', '1', '1', '0', '1', '0', '0'],
                              ['0', '0', '0', '0', '1', '0', '1', '1', '1', '0', '1', '0', '0'],
                              ['0', '0', '1', '0', '1', '1', '1', '0', '1', '0', '0', '0', '0']]
        start: float = time()
        print(Masker._evaluateLinePattern(matrix))
        print(f"Time taken : {time()-start:.6f} seconds.")
        exportQRCodeAsTextFile(matrix, name='qr_code_test_pattern')