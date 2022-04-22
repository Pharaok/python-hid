from __future__ import annotations

import string
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Iterator, Optional
from enum import Enum, IntEnum, IntFlag, auto


from hid.gadget import Gadget


class Modifier(IntFlag):
    NULL = 0x00
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
    KEYBOARD = {c: 0x00 + i for i, c in enumerate(['NULL', 'ERROR_POLL_OVER', 'POST_FAIL', 'ERROR_UNDEFINED'])}
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
    KEYBOARD |= {c: 0x46 + i for i, c in enumerate(['PRINT_SCREEN', 'SCROLL_LOCK', 'PAUSE', 'INSERT', 'HOME', 'PAGE_UP', 'DELETE',
                                                    'END', 'PAGE_DOWN', 'RIGHT_ARROW', 'LEFT_ARROW', 'DOWN_ARROW', 'UP_ARROW'])}
    KEYBOARD |= {'APPLICATION': 0x65}

    NUMPAD = {'NUM_LOCK': 0x53, 'CLEAR': 0x53}
    NUMPAD |= {c: 0x54 + i for i, c in enumerate('/*-=\n1234567890.')}
    NUMPAD |= {c: 0x58 + i for i, c in enumerate(['ENTER', 'END', 'DOWN_ARROW', 'PAGE_DOWN', 'LEFT_ARROW', 'RIGHT_ARROW'])}
    NUMPAD |= {c: 0x5F + i for i, c in enumerate(['HOME', 'UP_ARROW', 'PAGE_UP', 'INSERT', 'DELETE'])}

    NON_US = {
        '#': 0x32, '~': 0x32,
        '\\': 0x64, '|': 0x64,
    }


@dataclass
class KeyboardReport:
    MAX_KEYS = 6

    _mods: int = 0
    _keys: list[int] = field(default_factory=list)

    @property
    def mods(self) -> int:
        return self._mods

    @mods.setter
    def mods(self, v: int):
        if not 0 <= v < 256:
            raise ValueError
        self._mods = v

    @property
    def keys(self) -> list[int]:
        return self._keys + [KeyCode.KEYBOARD['NULL']] * (self.MAX_KEYS - len(self._keys))

    @keys.setter
    def keys(self, v: Sequence[int]) -> None:
        v = [x for x in v if x != KeyCode.KEYBOARD['NULL']]
        if len(v) > self.MAX_KEYS:
            raise IndexError
        if any([not 0 <= x < 256 for x in v]):
            raise ValueError
        self._keys = v

    def __iter__(self) -> Iterator[int]:
        return iter([self._mods, 0] + self.keys)

    def __str__(self) -> str:
        return ' '.join([f'{x:02X}' for x in self])


class Keyboard(Gadget):
    FUNCTION = {
        "protocol": "1",
        "subclass": "1",
        "report_length": "8",
        "report_desc": bytes([
            0x05, 0x01,
            0x09, 0x06,
            0xa1, 0x01,
            0x05, 0x07,
            0x19, 0xe0,
            0x29, 0xe7,
            0x15, 0x00,
            0x25, 0x01,
            0x75, 0x01,
            0x95, 0x08,
            0x81, 0x02,
            0x95, 0x01,
            0x75, 0x08,
            0x81, 0x03,
            0x95, 0x05,
            0x75, 0x01,
            0x05, 0x08,
            0x19, 0x01,
            0x29, 0x05,
            0x91, 0x02,
            0x95, 0x01,
            0x75, 0x03,
            0x91, 0x03,
            0x95, 0x06,
            0x75, 0x08,
            0x15, 0x00,
            0x25, 0x65,
            0x05, 0x07,
            0x19, 0x00,
            0x29, 0x65,
            0x81, 0x00,
            0xc0])
    }

    def __init__(self) -> None:
        super().__init__(functions=[self.FUNCTION])
        self.report = KeyboardReport()

    def send_report(self):
        with open("/dev/hidg0", "wb") as f:
            f.write(bytes(self.report))

    def write(self, text: str) -> None:
        for c in text:
            self.report.mods |= Modifier.from_char(c)
            self.report.keys.append(KeyCode.KEYBOARD[c])
            self.send_report()

            self.report.mods &= ~Modifier.from_char(c)
            self.report.keys.remove(KeyCode.KEYBOARD[c])
            self.send_report()
