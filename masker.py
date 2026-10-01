'''
This file contains code related to applying masks the QR Code matrix, and evaluating which is the best.
'''

from modules import Module
from math import floor
from typing import Callable

class Masker:
    '''Static class used for applying and evaluating masks'''

    MASK_FUNCTIONS: dict[int, Callable[[int, int], bool]] = {
                0: (lambda row, column: (row+column) % 2 == 0),
                1: (lambda row, column: row % 2 == 0),
                2: (lambda row, column: column % 3 == 0),
                3: (lambda row, column: (row+column) % 3 == 0),
                4: (lambda row, column: (floor(row/2) + floor(column/3)) % 2 == 0),
                5: (lambda row, column: ((row*column) % 2) + ((row*column) % 3) == 0),
                6: (lambda row, column: ((row*column) % 2) + ((row*column) % 3) % 2 == 0),
                7: (lambda row, column: ((row+column) % 2) + ((row*column) % 3) % 2 == 0),
            }
    PATTERN_BEFORE: list[str] = ['0', '0', '0', '0', '1', '0', '1', '1', '1', '0', '1']
    PATTERN_AFTER: list[str] = ['1', '0', '1', '1', '1', '0', '1', '0', '0', '0', '0']

    @staticmethod
    def applyBestMask(matrix: list[list]) -> tuple[list[list], int]:
        '''Finds the best mask for the given matrix and returns the new version with the applied mask, as well as the mask that was used.'''
        maskedMap: dict[int, list[list]] = {i:Masker.applyMask(i, matrix) for i in range(8)}
        bestScore: int = Masker.evaluateMatrix(maskedMap[0])
        bestMask: int = 0
        for i in range(1, 8):
            #exportQRCodeAsTextFile(maskedMap[i], name=f'qr_code_mask_{i}')
            score: int = Masker.evaluateMatrix(maskedMap[i])
            if score > bestScore:
                bestScore = score
                bestMask = i
        print(f'Mask used : {bestMask}')
        return maskedMap[bestMask], bestMask

    @staticmethod
    def applyMask(mask: int, matrix: list[list]) -> list[list]:
        '''Returns the new matrix with the given mask applied to it.'''
        newMatrix: list[list] = []
        maskFunction: Callable = Masker.MASK_FUNCTIONS[mask]
        for row in range(len(matrix)):
            newMatrix.append([])
            for column in range(len(matrix)):
                module: str | Module.ReservedModule = matrix[row][column]
                if not isinstance(module, Module.ReservedModule):
                    maskResult: bool = maskFunction(row, column)
                    if maskResult:
                        module: str = str(int(module == '0'))
                newMatrix[-1].append(module)
        return newMatrix

    @staticmethod
    def evaluateMatrix(matrix: list[list]) -> int:
        '''Evaluates and returns the score for the given matrix.'''
        score: int = Masker._evaluateRepeatingLines(matrix)
        score += Masker._evaluateSquares(matrix)
        score += Masker._evaluateLinePattern(matrix)
        score += Masker._evaluateModuleRatio(matrix)
        return score

    @staticmethod
    def _evaluateRepeatingLines(matrix: list[list]) -> int:
        '''Method that evaluates the given matrix based on the lines of repeating modules.'''
        score: int = 0
        size: int = len(matrix)
        for i in range(2):
            for row in range(size):
                consecutiveModuleCount: int = 1
                currentColor: str = ''
                for column in range(size):
                    color: str = Masker.getModuleColor(matrix, [row, column][i], [column, row][i])
                    if color == currentColor:
                        consecutiveModuleCount += 1
                        if consecutiveModuleCount == 5:
                            score += 3
                        elif consecutiveModuleCount > 5:
                            score += 1
                    else:
                        if column >= size - 4:
                            break
                        consecutiveModuleCount: int = 1
                        currentColor: str = color
        return score

    @staticmethod
    def _evaluateSquares(matrix: list[list]) -> int:
        '''Method that evaluates the given matrix based on the number of same colored squared.'''
        score: int = 0
        size: int = len(matrix)
        modulesToSkip: dict[tuple[int, int], bool] = {}
        for row in range(size-1):
            for column in range(size-1):
                skipModule: bool = modulesToSkip.get((row, column), False)
                if skipModule:
                    continue
                color: str = Masker.getModuleColor(matrix, row, column)
                colorRight: str = Masker.getModuleColor(matrix, row, column+1)
                colorBottom: str = Masker.getModuleColor(matrix, row+1, column)
                if color == colorRight == colorBottom:
                    if color == Masker.getModuleColor(matrix, row+1, column+1):
                        score += 3
                    else:
                        modulesToSkip[(row, column+1)] = True
                        modulesToSkip[(row+1, column)] = True
        return score

    @staticmethod
    def _evaluateLinePattern(matrix: list[list]) -> int:
        '''Method that evaluates the given matrix based on the presence of a specific pattern (B.W.B.B.B.W.B with W.W.W.W on either side).'''
        score: int = 0
        size: int = len(matrix)
        for i in range(2):
            for row in range(size):
                moduleSlice = [Masker.getModuleColor(matrix, [row, j][i], [j, row][i]) for j in range(11)]
                for column in range(1, size-10):
                    if moduleSlice == Masker.PATTERN_AFTER or moduleSlice == Masker.PATTERN_BEFORE:
                        score += 40
                    del moduleSlice[0]
                    moduleSlice.append(Masker.getModuleColor(matrix, [row, column+10][i], [column+10, row][i]))
                if moduleSlice == Masker.PATTERN_AFTER or moduleSlice == Masker.PATTERN_BEFORE:
                    score += 40
        return score

    @staticmethod
    def _evaluateModuleRatio(matrix: list[list]) -> int:
        '''Method that evaluates the given matrix based on the ratio of dark modules to white modules.'''
        size: int = len(matrix)
        totalModules: int = size**2
        darkModules: int = 0
        for row in range(size):
            for column in range(size):
                color: str = Masker.getModuleColor(matrix, row, column)
                darkModules += int(color)
        darkPercentage: int = int((darkModules/totalModules) * 100)
        previousMultiple: int = darkPercentage//5*5
        minusFifty: list[int] = [abs(previousMultiple-50)//5, abs(previousMultiple-45)//5]
        return min(minusFifty)*10

    @staticmethod
    def getModuleColor(matrix: list, row: int, column: int) -> str:
        '''Retrieves the color of the module at the given coordinates. Useful for automatically converting a Module.ReservedModule to its value.'''
        module: str | Module.ReservedModule = matrix[row][column]
        if isinstance(module, Module.ReservedModule):
            color: str = module.value
            if color == '2':
                color = '0'
        else:
            color: str = module
        return color

def exportQRCodeAsTextFile(qrCodeData: list[list], name: str = 'qr_code') -> None:
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