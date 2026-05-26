'''
This file contains classes used for communicating between processes during IPC.
'''

from enum import Enum, auto
from typing import Callable, Any
from dataclasses import dataclass, field
from qrerrors import QRError

class QRMessage(Enum):
    '''Enum used for storing messages to be sent over a multiprocessing queue during IPC'''
    ProcessStarted = auto()

@dataclass(frozen=False)
class QRTask:
    '''Task to be given to the QRWorker over a multiprocessing queue during IPC'''
    foo: Callable
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)

@dataclass(frozen=True)
class QRResult:
    '''Message to be sent over a multiprocessing queue during IPC once a task is finished'''
    wasSuccessful: bool
    data: Any | None = None
    error: QRError | None = None