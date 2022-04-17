from __future__ import annotations

import string
from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Iterator, Mapping, Optional

from hid.gadget import Gadget


class Modifiers(Mapping[str, int]):
    NULL = 0x00
    LEFT_CONTROL = 0x01
    LEFT_SHIFT = 0x02
    LEFT_ALT = 0x04
    LEFT_GUI = 0x08
    RIGHT_CONTROL = 0x10
    RIGHT_SHIFT = 0x20
    RIGHT_ALT = 0x40
    RIGHT_GUI = 0x80

    def __class_getitem__(cls, key: str) -> int:
        keys: dict[str, int] = defaultdict(lambda: cls.NULL)
        keys |= {k: v for k, v in cls.__dict__.items() if not k.startswith('_')}
        keys |= {c: cls.LEFT_SHIFT for c in string.ascii_uppercase}
        keys |= {c: cls.LEFT_SHIFT for c in ['!@#$%^&*()']}
        keys |= {c: cls.LEFT_SHIFT for c in ['_+{}|']}
        keys |= {c: cls.LEFT_SHIFT for c in [':"~<>?']}

        return keys[key]


class KeyCodes(Mapping[str, int]):
    _kb = {c: 0x04 + i for i, c in enumerate(string.ascii_lowercase)}
    _kb |= {c: 0x04 + i for i, c in enumerate(string.ascii_uppercase)}
    _kb |= {c: 0x1E + i for i, c in enumerate('1234567890')}
    _kb |= {c: 0x1A + i for i, c in enumerate('!@#$%^&*()')}
    _kb |= {c: 0x28 + i for i, c in enumerate('\n\x1B\x08\x2A\t ')}
    _kb |= {c: 0x2D + i for i, c in enumerate('-=[]\\')}
    _kb |= {c: 0x2D + i for i, c in enumerate('_+{}|')}
    _kb |= {c: 0x33 + i for i, c in enumerate(";'`,./")}
    _kb |= {c: 0x33 + i for i, c in enumerate(':"~<>?')}
    _kb |= {'\x7F': 0x4C}

    _np = {c: 0x54 + i for i, c in enumerate('\\*-+\n1234567890.')}

    def __class_getitem__(cls, key: str) -> int:
        return cls.keyboard(key)

    @classmethod
    def keyboard(cls, key: str) -> int:
        keys: dict[str, int] = {k: v for k, v in cls.__dict__.items()
                                if not k.startswith('_')}
        keys |= cls._kb
        return keys[key]

    @classmethod
    def numpad(cls, key: str) -> int:
        keys: dict[str, int] = {k: v for k, v in cls.__dict__.items()
                                if not k.startswith('_')}
        keys |= cls._kb
        keys |= cls._np
        return keys[key]

    NULL = 0x00
    ERROR_ROLL_OVER = 0x01
    POST_FAIL = 0x02
    ERROR_UNDEFINED = 0x03
    ENTER = 0x28
    ESCAPE = 0x29
    BACKSPACE = 0x2A
    SPACEBAR = 0x2C
    CAPS_LOCK = 0x39
    F1 = 0x3A
    F2 = 0x3B
    F3 = 0x3C
    F4 = 0x3D
    F5 = 0x3E
    F6 = 0x3F
    F7 = 0x40
    F8 = 0x41
    F9 = 0x42
    F10 = 0x43
    F11 = 0x44
    F12 = 0x45
    PRINT_SCREEN = 0x46
    SCROLL_LOCK = 0x47
    PAUSE = 0x48
    INSERT = 0x49
    HOME = 0x4A
    PAGE_UP = 0x4B
    DELETE = 0x4C
    END = 0x4D
    PAGE_DOWN = 0x4E
    RIGHT_ARROW = 0x4F
    LEFT_ARROW = 0x50
    DOWN_ARROW = 0x51
    UP_ARROW = 0x52
    NUM_LOCK = 0x53
    NUMPAD_DIV = 0x54
    NUMPAD_MUL = 0x55
    NUMPAD_SUB = 0x56
    NUMPAD_ADD = 0x57
    NUMPAD_ENTER = 0x58
    NUMPAD_END = 0x59
    NUMPAD_DOWN_ARROW = 0x5A
    NUMPAD_PAGE_DOWN = 0x5B
    NUMPAD_LEFT_ARROW = 0x5C
    NUMPAD_RIGHT_ARROW = 0x5E
    NUMPAD_HOME = 0x5F
    NUMPAD_UP_ARROW = 0x60
    NUMPAD_PAGE_UP = 0x61
    NUMPAD_INSERT = 0x62
    NUMPAD_PERIOD = 0x63
    NUMPAD_DELETE = 0x63
    APPLICATION = 0x65


@dataclass
class KeyboardReport():
    MAX_KEYS = 6

    _mods: int = 0
    _keys: list[int] = field(default_factory=list)

    def __init__(self,
                 mods: int = 0,
                 keys: Optional[Sequence[int]] = None,
                 update_callback: Callable[[], None] = lambda: None) -> None:
        self._update = update_callback

        self.mods = mods

        if keys is None:
            keys = []
        self.keys = keys  # type: ignore

    @property
    def mods(self) -> int:
        return self._mods

    @mods.setter
    def mods(self, v: int):
        if not 0 <= v < 256:
            raise ValueError
        self._mods = v
        self._update()

    @property
    def keys(self) -> list[int]:
        return self._keys + [KeyCodes.NULL] * (self.MAX_KEYS - len(self._keys))

    @keys.setter
    def keys(self, v: Sequence[int]) -> None:
        v = [x for x in v if x != KeyCodes.NULL]
        if len(v) > self.MAX_KEYS:
            raise IndexError
        if any([not 0 <= x < 256 for x in v]):
            raise ValueError
        self._keys = v
        self._update()

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
            0xc0
        ])
    }

    def __init__(self) -> None:
        super().__init__(functions=[self.FUNCTION])
        self.report = KeyboardReport(update_callback=self._update)

    def __enter__(self) -> Keyboard:
        super().__enter__()
        return self

    def _update(self):
        with open("/dev/hidg0", "wb") as f:
            f.write(bytes(self.report))
