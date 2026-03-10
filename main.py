import os, random

EC = {'L':7,
      'M':15,
      'Q':25,
      'H':30}

class QRCode:
    def __init__(self, path):
        with open(path, mode='r') as file:
            self.contents = file.read()

    def chooseMode(self):
        pass


def reedSolomon(values):
    polynomial = ''
    for n in range(len(values)):
        polynomial += f'{values[n]}*x**{n}+'
    polynomial = polynomial[:-1]
    print(polynomial)
    def p(x):
        if 0 <= x <= 255:
            return eval(polynomial)
        else:
            raise ValueError('x must be between 0 and 255 inclusive!')
    return p



























