from __future__ import annotations
import re

import string
from collections.abc import Sequence, MutableSequence
from dataclasses import dataclass, field
from typing import Iterator, Optional
from enum import IntFlag, auto


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
    NULL = 0x00

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


class KeyList(MutableSequence[int]):
    RESERVED = {*range(0, 4)}

    def __init__(self, keys: Optional[Sequence[int]] = None, max_len: int = 6) -> None:
        self.max_len = max_len
        self._list = []

        if keys is None:
            keys = []
        for i, key in enumerate(keys):
            self.__setitem__(i, key)

    def __getitem__(self, i: int) -> int:
        if len(self._list) > self.max_len:
            return KeyCode.KEYBOARD['ERROR_ROLL_OVER']
        if self.max_len > i >= len(self._list):
            return KeyCode.NULL
        return self._list.__getitem__(i)

    def __setitem__(self, i: int, v: int) -> None:
        if not 0 < v < 256:
            raise ValueError
        if v in self.RESERVED or v in self._list:
            return

        self._list.__setitem__(i, v)

    def __delitem__(self, i: int) -> None:
        self._list.__delitem__(i)

    def __len__(self) -> int:
        return self.max_len

    def insert(self, i: int, v: int) -> int:
        if not 0 <= v < 256:
            raise ValueError
        if v in self.RESERVED or v in self._list:
            return

        self._list.insert(i, v)

    def __contains__(self, v: int) -> bool:
        return self._list.__contains__(v)

    def index(self, v: int) -> int:
        return self._list.index(v)


@dataclass
class KeyboardReport:
    _mods: int = 0
    _keys: KeyList = field(default_factory=KeyList)

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
        return self._keys

    @keys.setter
    def keys(self, v: Sequence[int]) -> None:
        self._keys = KeyList(v)

    def __iter__(self) -> Iterator[int]:
        return iter([self._mods, 0] + list(self._keys))

    def __str__(self) -> str:
        return ' '.join([f'{x:02X}' for x in self])


class Keyboard:
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

    def __init__(self, gadget: Optional[Gadget] = None) -> None:
        if gadget is None:
            gadget = Gadget()
        self.gadget = gadget
        self.function = gadget.add_function(self.FUNCTION)
        self.report = KeyboardReport()

    def send_report(self) -> None:
        if not self.gadget.enabled:
            raise Exception
        d = self.function['dev']
        d = d.strip()
        d = d[d.find(':') + 1:]
        with open(f"/dev/hidg{d}", "wb") as f:
            f.write(bytes(self.report))

    def write(self, text: str) -> None:
        for c in text:
            self.report.mods |= Modifier.from_char(c)
            self.report.keys.append(KeyCode.KEYBOARD[c])
            self.send_report()

            self.report.mods &= ~Modifier.from_char(c)
            self.report.keys.remove(KeyCode.KEYBOARD[c])
            self.send_report()
