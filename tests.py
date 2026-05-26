from reed_solomon import Polynomial, GaloisField

testPolynomial: bool = False
testGalois: bool = True
if (testPolynomial):
    pol1 = Polynomial({
        '2': -2,
        '3': -4,
        '1': 2,
        '4': 8,
        '0': 3
    })
    pol2 = Polynomial({
        '6': 6,
        '4': -3,
        '2': -3,
        '1': -9,
        '0': 7
    })
    print(pol1)
    print(pol2)
    print(pol1 + pol2)
    print(pol2 + pol1)
    print(pol1 - pol2)
if (testGalois):
    gVals: list[int] = GaloisField.GALOIS_VALS
    print(GaloisField.mul(gVals[170], gVals[164]))