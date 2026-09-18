import application
import qrworker
import qrdata  
import qrerrors
import reed_solomon
import IPC_coms
from time import time

testPolynomial: bool = False
testGeneratorPolynomials: bool = False
Polynomial = reed_solomon.Polynomial
testGaloisExpToVal: bool = False
testGaloisValToExp: bool = False
testGaloisMul: bool = False
GaloisField = reed_solomon.GaloisField
if (testPolynomial):
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
    print(Polynomial.getGenerator(3))
    print(Polynomial.getGenerator(7))
    print(Polynomial.getGenerator(34))
    print(Polynomial.getGenerator(125))
    print(Polynomial.getGenerator(10))
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