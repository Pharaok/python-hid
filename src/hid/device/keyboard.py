from __future__ import annotations

import string
from ctypes import Structure, c_ubyte

from hid.report import ProtocolCode, SubclassCode, ReportDescriptor
from hid.report.item import *
from hid.report.usage import UsagePages
from . import HIDDevice


class Modifier(IntFlag):
    NULL = 0
    LEFT_CONTROL = auto()
    LEFT_SHIFT = auto()
    LEFT_ALT = auto()
    LEFT_GUI = auto()
    RIGHT_CONTROL = auto()
    RIGHT_SHIFT = auto()
    RIGHT_ALT = auto()
    RIGHT_GUI = auto()

    @classmethod
    def from_char(cls, char: str, left: bool = True) -> Modifier:
        if len(char) != 1:
            raise ValueError
        if char in string.ascii_uppercase + '!@#$%^&*()_+{}|:"~<>?':
            return cls.LEFT_SHIFT if left else cls.RIGHT_SHIFT
        else:
            return cls.NULL


class KeyCode:
    KEYBOARD = {c: 0x01 + i for i, c in enumerate(['ERROR_ROLL_OVER', 'POST_FAIL', 'ERROR_UNDEFINED'])}
    KEYBOARD |= {c: 0x04 + i for i, c in enumerate(string.ascii_lowercase)}
    KEYBOARD |= {c: 0x04 + i for i, c in enumerate(string.ascii_uppercase)}
    KEYBOARD |= {c: 0x1E + i for i, c in enumerate('1234567890')}
    KEYBOARD |= {c: 0x1E + i for i, c in enumerate('!@#$%^&*()')}
    KEYBOARD |= {c: 0x28 + i for i, c in enumerate(['ENTER', 'ESCAPE', 'BACKSPACE', 'TAB', 'SPACEBAR'])}
    KEYBOARD |= {c: 0x28 + i for i, c in enumerate('\n\x1b\x08\t ')}
    KEYBOARD |= {c: 0x2D + i for i, c in enumerate('-=[]\\;\'`,./')}
    KEYBOARD |= {c: 0x2D + i for i, c in enumerate('_+{}|:"~<>?')}
    KEYBOARD |= {'CAPS_LOCK': 0x39}
    KEYBOARD |= {f'F{1 + i}': 0x3A + i for i in range(12)}
    KEYBOARD |= {c: 0x46 + i for i, c in enumerate(['PRINT_SCREEN', 'SCROLL_LOCK', 'PAUSE', 'INSERT', 'HOME',
                                                    'PAGE_UP', 'DELETE', 'END', 'PAGE_DOWN', 'RIGHT_ARROW',
                                                    'LEFT_ARROW', 'DOWN_ARROW', 'UP_ARROW'])}
    KEYBOARD |= {'APPLICATION': 0x65}

    NUMPAD = {'NUM_LOCK': 0x53, 'CLEAR': 0x53}
    NUMPAD |= {c: 0x54 + i for i, c in enumerate('/*-=\n1234567890.')}
    NUMPAD |= {c: 0x58 + i for i, c in enumerate(['ENTER', 'END', 'DOWN_ARROW', 'UP_ARROW',
                                                  'PAGE_DOWN', 'LEFT_ARROW', 'RIGHT_ARROW'])}
    NUMPAD |= {c: 0x5F + i for i, c in enumerate(['HOME', 'UP_ARROW', 'PAGE_UP', 'INSERT', 'DELETE'])}

    NON_US = {
        '#': 0x32, '~': 0x32,
        '\\': 0x64, '|': 0x64,
    }


class KeyboardReport(Structure):
    _fields_ = [('mods', c_ubyte),
                ('', c_ubyte),
                ('keys', (c_ubyte * 6))]


class Keyboard(HIDDevice):
    DESCRIPTOR = ReportDescriptor((
        UsagePage(UsagePages.GENERIC_DESKTOP),
        Usage(6),
        Collection(CollectionType.APPLICATION),
        (
            UsagePage(UsagePages.KEYBOARD),
            UsageMinimum(0xe0),
            UsageMaximum(0xe7),
            LogicalMinimum(0),
            LogicalMaximum(1),
            ReportSize(1),
            ReportCount(8),
            Input(DataFlag.VARIABLE),

            ReportCount(1),
            ReportSize(8),
            Input(DataFlag.CONSTANT, DataFlag.VARIABLE),

            ReportCount(5),
            ReportSize(1),
            UsagePage(8),
            UsageMinimum(1),
            UsageMaximum(5),
            Output(DataFlag.VARIABLE),

            ReportCount(1),
            ReportSize(3),
            Output(DataFlag.CONSTANT, DataFlag.VARIABLE),

            ReportCount(6),
            ReportSize(8),
            LogicalMinimum(0),
            LogicalMaximum(0x65),
            UsagePage(7),
            UsageMinimum(0),
            UsageMaximum(0x65),
            Input(),
        ),
        EndCollection()
    ))
    PROTOCOL = ProtocolCode.KEYBOARD
    SUBCLASS = SubclassCode.BOOT_INTERFACE

    def write(self, text: str) -> None:
        for c in text:
            self.send_report(KeyboardReport(mods=Modifier.from_char(c), keys=(c_ubyte * 6)(KeyCode.KEYBOARD[c])))
            self.send_report(KeyboardReport())
