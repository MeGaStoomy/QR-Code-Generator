'''
This file contains all the code related to placing modules inside of the QR Code matrix, as well as creating it.
'''

from enum import Enum
from itertools import product
from qrdata import getAlignPosList

class Module:
    '''Static class used for code related to module placement.'''
    class ReservedModule(Enum):
        '''Represents a reserved (Black or White) Module, such as those for timing patterns, alignment patterns, etc.'''
        WHITE = '0'
        BLACK = '1'
        RESERVED = '2'

    @staticmethod
    def addFinderPatterns(matrix: list[list]) -> None:
        '''Adds all three finder patterns to the given square matrix.'''
        dimensions: int = len(matrix)
        Module._addSingleFinderPattern(matrix, 3, 3)
        Module._addSingleFinderPattern(matrix, dimensions-4, 3)
        Module._addSingleFinderPattern(matrix, 3, dimensions-4)

    @staticmethod
    def _addSingleFinderPattern(matrix: list[list], x: int, y: int) -> None:
        '''Helper method that adds a single finder pattern at the given x and y coordinates, anchored on the center, starting at 0.'''
        # The following draws the outer 7x7 black borders.
        for yDiff in [-3, 3]:
            for xDiff in range(-3, 4):
                matrix[y+yDiff][x+xDiff] = Module.ReservedModule.BLACK
        for xDiff in [-3, 3]:
            for yDiff in range(-2, 3):
                matrix[y+yDiff][x+xDiff] = Module.ReservedModule.BLACK
        # The following draws the inner 3x3 black square.
        for yDiff in range(-1, 2):
            for xDiff in range(-1, 2):
                matrix[y+yDiff][x+xDiff] = Module.ReservedModule.BLACK
        # The following draws the inner 5x5 white borders.
        for yDiff in [-2, 2]:
            for xDiff in range(-2, 3):
                matrix[y+yDiff][x+xDiff] = Module.ReservedModule.WHITE
        for xDiff in [-2, 2]:
            for yDiff in range(-1, 2):
                matrix[y+yDiff][x+xDiff] = Module.ReservedModule.WHITE

    @staticmethod
    def addSeparators(matrix: list[list]) -> None:
        '''Adds all three separators to the given square matrix.'''
        dimensions: int = len(matrix)
        # The following adds all vertical separator lines.
        for y in range(8):
            matrix[y][7] = Module.ReservedModule.WHITE
            matrix[y][dimensions-8] = Module.ReservedModule.WHITE
            matrix[y+dimensions-8][7] = Module.ReservedModule.WHITE
        # The following adds all horizontal separator lines.
        for x in range(8):
            matrix[7][x] = Module.ReservedModule.WHITE
            matrix[7][x+dimensions-8] = Module.ReservedModule.WHITE
            matrix[dimensions-8][x] = Module.ReservedModule.WHITE

    @staticmethod
    def addAlignmentPattern(matrix: list[list], version: int) -> None:
        '''Adds all the alignment patterns to the given matrix.'''
        for coordinates in product(getAlignPosList(version), repeat=2):
            x: int = coordinates[0]
            y: int = coordinates[1]
            print(x,y)
            if not isinstance(matrix[y][x], Module.ReservedModule):
                Module._addSingleAlignment(matrix, *coordinates)

    @staticmethod
    def _addSingleAlignment(matrix: list[list], x: int, y: int) -> None:
        '''Helper method that adds a single alignment pattern to the given matrix at the given x and y coordinates.'''
        # The following adds the outer black borders.
        for yDiff in [-2, 2]:
            for xDiff in range(-2, 3):
                matrix[y+yDiff][x+xDiff] = Module.ReservedModule.BLACK
        for xDiff in [-2, 2]:
            for yDiff in range(-1, 2):
                matrix[y+yDiff][x+xDiff] = Module.ReservedModule.BLACK
        # The following adds the upper and lower inner white borders.
        for yDiff in [-1, 1]:
            for xDiff in range(-1, 2):
                matrix[y+yDiff][x+xDiff] = Module.ReservedModule.WHITE
        # The following adds the remaining three modules.
        matrix[y][x-1] = Module.ReservedModule.WHITE
        matrix[y][x] = Module.ReservedModule.BLACK
        matrix[y][x+1] = Module.ReservedModule.WHITE

    @staticmethod
    def addTimingPatterns(matrix: list[list]) -> None:
        '''Adds the two timing patterns to the given matrix.'''
        for x in range(8, len(matrix)-7, 2):
            matrix[6][x] = Module.ReservedModule.BLACK
            matrix[6][x+1] = Module.ReservedModule.WHITE
        for y in range(8, len(matrix)-7, 2):
            matrix[y][6] = Module.ReservedModule.BLACK
            matrix[y+1][6] = Module.ReservedModule.WHITE

    @staticmethod
    def addReservedAreas(matrix: list[list], version: int) -> None:
        '''Adds all the reserved areas.'''
        dimensions: int = len(matrix)
        # The following adds the reserved horizontal stripes.
        for x in range(6):
            matrix[8][x] = Module.ReservedModule.RESERVED
        for x in [7, 8]:
            matrix[8][x] = Module.ReservedModule.RESERVED
        for x in range(dimensions-8, dimensions):
            matrix[8][x] = Module.ReservedModule.RESERVED
        # The following adds the reserved vertical stripes.
        for y in range(6):
            matrix[y][8] = Module.ReservedModule.RESERVED
        for y in [7, 8]:
            matrix[y][8] = Module.ReservedModule.RESERVED
        for y in range(dimensions-8, dimensions):
            matrix[y][8] = Module.ReservedModule.RESERVED
        # The following adds the single dark module.
        matrix[4*version + 9][8] = Module.ReservedModule.BLACK
        if version > 6:
            # The following adds the additional top right reserved block.
            topLeftCornerX: int = dimensions-11
            topLeftCornery: int = 0
            for yDiff in range(0, 6):
                for xDiff in range(0, 3):
                    matrix[topLeftCornery+yDiff][topLeftCornerX+xDiff] = Module.ReservedModule.RESERVED
            # The following adds the additional bottom left reserved block.
            topLeftCornerX: int = 0
            topLeftCornery: int = dimensions-11
            for yDiff in range(0, 3):
                for xDiff in range(0, 6):
                    matrix[topLeftCornery+yDiff][topLeftCornerX+xDiff] = Module.ReservedModule.RESERVED

    @staticmethod
    def placeData(data: list[str], matrix: list[list]) -> None:
        '''Places the rawData into the matrix.'''
        # This method places the data bits in the reversed order (L->R instead of L<-R) as it makes detecting the vertical timing pattern easier.
        for x in range(1, 6, 2):
            upwards: bool = x%4 == 1
            Module._drawCollumn(data, matrix, x, upwards)
        for x in range(8, len(matrix), 2):
            upwards: bool = x%4 == 2
            Module._drawCollumn(data, matrix, x, upwards)
        print(data)

    @staticmethod
    def _drawCollumn(data: list[str], matrix: list[list], x: int, upwards: bool = True) -> None:
        '''Helper method that draws a 2-module wide vertical line at the given y coordinate (anchored on the right side of the collumn).'''
        if upwards:
            y: int = len(matrix)-1
            yDelta: int = -1
        else:
            y: int = 0
            yDelta: int = 1
        while 0 <= y <= len(matrix)-1:
            for newX in [x, x-1]:
                if not isinstance(matrix[y][newX], Module.ReservedModule):
                    matrix[y][newX] = data.pop()
            y += yDelta