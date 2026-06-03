import application
import qrworker
import qrdata  
import qrerrors
import reed_solomon
import IPC_coms

testPolynomial: bool = True
testGalois: bool = False
if (testPolynomial):
    Polynomial = reed_solomon.Polynomial
    pol1: Polynomial = Polynomial([210])
    print(pol1)
    print(pol1.__repr__())
    print(Polynomial._getStrExp(1234567890982459135278))
    pol2: Polynomial = Polynomial([153, 94, -15, 3, 0, 0, 13])
    pol3: Polynomial = Polynomial([1, 0, 0, 0, 0, 0, 0, 0, 9, 3])
    pol4: Polynomial = Polynomial([])
    pol5: Polynomial = Polynomial([0,0,0,0,0])
    print(pol2)
    print(pol3)
    print(pol4)
    print(pol5)
if (testGalois):
    GaloisField = reed_solomon.GaloisField
    gVals: list[int] = GaloisField.GALOIS_VALS
    print(GaloisField.mul(gVals[170], gVals[164]))