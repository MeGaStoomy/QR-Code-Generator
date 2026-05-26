'''
This file is basically an enum of custom errors that might occur during QR Code generation.
'''

from enum import Enum, auto

class QRError(Enum):
    ModeError = auto()
    VersionError = auto()
    # used when there is too much data to encode for any version of a qr code
    EncodeError = auto()