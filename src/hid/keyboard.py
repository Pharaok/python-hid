from __future__ import annotations

import string
from collections import defaultdict
from typing import Optional, SupportsInt


class Modifier():
    def __init__(self, x: SupportsInt = 0) -> None:
        self._mod = int(x)

    def __int__(self) -> int:
        return self._mod

    def __repr__(self) -> str:
        return repr(int(self))

    def __format__(self, x: str) -> str:
        return format(int(self), x)

    def __bool__(self) -> bool:
        return bool(int(self))

    def __invert__(self) -> Modifier:
        return Modifier(~int(self))

    def __or__(self, x:  SupportsInt) -> Modifier:
        return Modifier(int(self) | int(x))

    def __ror__(self, x: SupportsInt) -> Modifier:
        return Modifier(int(x) | int(self))

    def __and__(self, x: SupportsInt) -> Modifier:
        return Modifier(int(self) & int(x))

    def __rand__(self, x: SupportsInt) -> Modifier:
        return Modifier(int(x) & int(self))

    def __xor__(self, x: SupportsInt) -> Modifier:
        return Modifier(int(self) ^ int(x))

    def __rxor__(self, x: SupportsInt) -> Modifier:
        return Modifier(int(x) ^ int(self))

    def __rshift__(self, x: SupportsInt) -> Modifier:
        return Modifier(int(self) >> int(x))

    def __lshift__(self, x: SupportsInt) -> Modifier:
        return Modifier(int(self) << int(x))


class Modifiers():
    NULL = Modifier(0x00)
    LEFT_CONTROL = Modifier(0x01)
    LEFT_SHIFT = Modifier(0x02)
    LEFT_ALT = Modifier(0x04)
    LEFT_GUI = Modifier(0x08)
    RIGHT_CONTROL = Modifier(0x10)
    RIGHT_SHIFT = Modifier(0x20)
    RIGHT_ALT = Modifier(0x40)
    RIGHT_GUI = Modifier(0x80)

    def __class_getitem__(cls, key: str) -> Modifier:
        keys = defaultdict(lambda: cls.NULL)
        keys |= {k: v for k, v in cls.__dict__.items() if not k.startswith('_')}
        keys |= {chr(ord('A') + i): cls.LEFT_SHIFT for i in range(26)}
        keys |= {c: cls.LEFT_SHIFT for c in ['!@#$%^&*()']}
        keys |= {c: cls.LEFT_SHIFT for c in ['_+{}|']}
        keys |= {c: cls.LEFT_SHIFT for c in [':"~<>?']}

        return Modifier(keys[key])


class ModifierBitArray(Modifier):
    def press(self, *mods: SupportsInt) -> None:
        for mod in mods:
            if self & mod:
                raise ValueError(
                    f"Cannot release already released modifier: {mod}")
            self |= mod

    def release(self, *mods: SupportsInt) -> None:
        for mod in mods:
            if not self & mod:
                raise ValueError(
                    f"Cannot release already released modifier: {mod}")
            self &= ~mod


class KeyCode():
    def __init__(self, x: SupportsInt = 0) -> None:
        self._key_code = int(x)

    def __repr__(self) -> str:
        return repr(int(self))

    def __format__(self, x: str) -> str:
        return format(int(self), x)

    def __int__(self) -> int:
        return self._key_code

    def __eq__(self, x: SupportsInt) -> bool:
        return int(self) == int(x)


class KeyArray():
    LEN = 6

    def __init__(self, keys: Optional[list[SupportsInt]] = None) -> None:
        keys = keys or []
        self._keys = [KeyCode() for _ in range(self.LEN)]
        self._i = 0
        self.press(*keys)

    def press(self, *keys: SupportsInt) -> None:
        for key in keys:
            if key == KeyCodes.NULL:
                continue
            elif key in self:
                continue
            self._keys[self._i] = key
            self._i += 1

    def release(self, *keys: SupportsInt) -> None:
        # Replace keys to release with NONE KeyCode
        for key in keys:
            if key == KeyCodes.NULL:
                continue
            try:
                i = self._keys.index(key)
            except ValueError:
                i = None
            if i is None:
                continue
            self._keys[i] = KeyCodes.NULL
        # Move all NONE KeyCodes to the end
        self._keys.sort(key=lambda x: x == KeyCodes.NULL)

    def __iter__(self) -> list[int]:
        return iter(self._keys)

    def __repr__(self) -> str:
        return repr(self._keys)

    def __format__(self, x: str) -> str:
        return format(list(self), x)


class KeyCodes():
    _kb = {None: 0x00}
    _kb |= {c: 0x04 + i for i, c in enumerate(string.ascii_lowercase)}
    _kb |= {c: 0x04 + i for i, c in enumerate(string.ascii_uppercase)}
    _kb |= {c: 0x1E + i for i, c in enumerate('1234567890')}
    _kb |= {c: 0x1A + i for i, c in enumerate('!@#$%^&*()')}
    _kb |= {c: 0x28 + i for i, c in enumerate('\n\x1B\x08\x2A\t ')}
    _kb |= {c: 0x2D + i for i, c in enumerate('-=[]\\')}
    _kb |= {c: 0x2D + i for i, c in enumerate('_+{}|')}
    _kb |= {c: 0x33 + i for i, c in enumerate(";'`,./")}
    _kb |= {c: 0x33 + i for i, c in enumerate(':"~<>?')}
    _kb |= {'\x7F': 0x4C}

    _np = {c: 0x54 + i for i, c in enumerate('\*-+\n1234567890.')}

    def __class_getitem__(cls, key: str):
        return cls.keyboard(key)

    @classmethod
    def keyboard(cls, key: str):
        keys = {k: v for k, v in cls.__dict__.items()
                if not k.startswith('_')}
        keys |= cls._kb
        return KeyCode(keys[key])

    @classmethod
    def numpad(cls, key: str):
        keys = {k: v for k, v in cls.__dict__.items()
                if not k.startswith('_')}
        keys |= cls._kb
        keys |= cls._np
        return KeyCode(keys[key])

    NULL = KeyCode(0x00)
    ERROR_ROLL_OVER = KeyCode(0x01)
    POST_FAIL = KeyCode(0x02)
    ERROR_UNDEFINED = KeyCode(0x03)
    ENTER = KeyCode(0x28)
    ESCAPE = KeyCode(0x29)
    BACKSPACE = KeyCode(0x2A)
    SPACEBAR = KeyCode(0x2C)
    CAPS_LOCK = KeyCode(0x39)
    F1 = KeyCode(0x3A)
    F2 = KeyCode(0x3B)
    F3 = KeyCode(0x3C)
    F4 = KeyCode(0x3D)
    F5 = KeyCode(0x3E)
    F6 = KeyCode(0x3F)
    F7 = KeyCode(0x40)
    F8 = KeyCode(0x41)
    F9 = KeyCode(0x42)
    F10 = KeyCode(0x43)
    F11 = KeyCode(0x44)
    F12 = KeyCode(0x45)
    PRINT_SCREEN = KeyCode(0x46)
    SCROLL_LOCK = KeyCode(0x47)
    PAUSE = KeyCode(0x48)
    INSERT = KeyCode(0x49)
    HOME = KeyCode(0x4A)
    PAGE_UP = KeyCode(0x4B)
    DELETE = KeyCode(0x4C)
    END = KeyCode(0x4D)
    PAGE_DOWN = KeyCode(0x4E)
    RIGHT_ARROW = KeyCode(0x4F)
    LEFT_ARROW = KeyCode(0x50)
    DOWN_ARROW = KeyCode(0x51)
    UP_ARROW = KeyCode(0x52)
    NUM_LOCK = KeyCode(0x53)
    NUMPAD_DIV = KeyCode(0x54)
    NUMPAD_MUL = KeyCode(0x55)
    NUMPAD_SUB = KeyCode(0x56)
    NUMPAD_ADD = KeyCode(0x57)
    NUMPAD_ENTER = KeyCode(0x58)
    NUMPAD_END = KeyCode(0x59)
    NUMPAD_DOWN_ARROW = KeyCode(0x5A)
    NUMPAD_PAGE_DOWN = KeyCode(0x5B)
    NUMPAD_LEFT_ARROW = KeyCode(0x5C)
    NUMPAD_RIGHT_ARROW = KeyCode(0x5E)
    NUMPAD_HOME = KeyCode(0x5F)
    NUMPAD_UP_ARROW = KeyCode(0x60)
    NUMPAD_PAGE_UP = KeyCode(0x61)
    NUMPAD_INSERT = KeyCode(0x62)
    NUMPAD_PERIOD = KeyCode(0x63)
    NUMPAD_DELETE = KeyCode(0x63)
    APPLICATION = KeyCode(0x65)


class KeyboardReport():
    pass


class Keyboard(KeyboardReport):
    pass
