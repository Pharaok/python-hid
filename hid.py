from __future__ import annotations

from collections import defaultdict
from typing import Any, Optional, Sequence


class Modifier():
    def __init__(self, x: Modifier | int = 0) -> None:
        self._mod = x._mod if isinstance(x, Modifier) else x

    def __str__(self) -> str:
        return str(self._mod)

    def __format__(self, x: str) -> str:
        return format(self._mod, x)

    def __bool__(self):
        return bool(self._mod)

    def __invert__(self) -> Modifier:
        return Modifier(~self._mod)

    def __or__(self, x: Modifier | int) -> Modifier:
        n = x._mod if isinstance(x, Modifier) else x
        return Modifier(self._mod | n)

    def __ror__(self, x: Modifier | int) -> Modifier:
        return self | x

    def __and__(self, x: Modifier | int) -> Modifier:
        n = x._mod if isinstance(x, Modifier) else x
        return Modifier(self._mod & n)

    def __rand__(self, x: Modifier | int) -> Modifier:
        return self & x

    def __xor__(self, x: Modifier | int) -> Modifier:
        return Modifier(self._mod ^ (x._mod if isinstance(x, Modifier) else x))

    def __rxor__(self, x: Modifier | int) -> Modifier:
        return self ^ x

    def __rshift__(self, x: int) -> Modifier:
        return Modifier(self._mod >> x)

    def __lshift__(self, x: int) -> Modifier:
        return Modifier(self._mod << x)


class Modifiers():
    NONE = Modifier(0x00)
    LEFT_CONTROL = Modifier(0x01)
    LEFT_SHIFT = Modifier(0x02)
    LEFT_ALT = Modifier(0x04)
    LEFT_GUI = Modifier(0x08)
    RIGHT_CONTROL = Modifier(0x10)
    RIGHT_SHIFT = Modifier(0x20)
    RIGHT_ALT = Modifier(0x40)
    RIGHT_GUI = Modifier(0x80)

    def __class_getitem__(cls, key: str) -> Modifier:
        keys = defaultdict(lambda: cls.NONE)
        keys |= {k: v for k, v in cls.__dict__.items()}
        keys |= {chr(ord('A') + i): cls.LEFT_SHIFT for i in range(26)}
        keys |= {c: cls.LEFT_SHIFT for c in ['!@#$%^&*()']}
        keys |= {c: cls.LEFT_SHIFT for c in ['_+{}|']}
        keys |= {c: cls.LEFT_SHIFT for c in [':"~<>?']}

        return Modifier(keys[key])


class ModifierBitField(Modifier):
    def press(self, *mods: Modifier | int) -> None:
        for mod in mods:
            if self & mod:
                raise ValueError(
                    f"Cannot release already released modifier: {mod}")
            self |= mod

    def release(self, *mods: Modifier | int) -> None:
        for mod in mods:
            if self & ~mod:
                raise ValueError(
                    f"Cannot release already released modifier: {mod}")
            self &= ~mod


class KeyCode():
    def __init__(self, x: KeyCode | int = 0) -> None:
        self._key_code = x._key_code if isinstance(x, KeyCode) else x

    def __str__(self) -> str:
        return str(self._key_code)

    def __format__(self, x: str) -> str:
        return format(self._key_code, x)

    def __eq__(self, x: Any) -> bool:
        return self._key_code == (x._key_code if isinstance(x, KeyCode) else x)


class KeyArray():
    LEN = 6

    def __init__(self, keys: Optional[KeyArray | Sequence[KeyCode]] = None) -> None:
        if keys is None:
            keys = []
        elif isinstance(keys, KeyArray):
            keys = keys._keys[:keys._i]
        self._keys = [KeyCode() for _ in range(self.LEN)]
        self._i = 0
        self.press(*keys)

    def press(self, *keys: KeyCode) -> None:
        for key in keys:
            if key in self._keys:
                continue
            self._keys[self._i] = key
            self._i += 1

    def release(self, *keys: KeyCode) -> None:
        # Replace keys to release with NONE KeyCode
        for key in keys:
            try:
                i = self._keys.index(key)
            except ValueError:
                i = None
            if i is None:
                continue
            self._keys[i] = KeyCodes.NONE
        # Move all NONE KeyCodes to the end
        self._keys.sort(key=lambda x: x == KeyCodes.NONE)

    def __str__(self) -> str:
        return f"[{', '.join([str(k) for k in self._keys])}]"

    def __format__(self, x: str) -> str:
        return format(self._keys, x)


class KeyCodes():
    def __class_getitem__(cls, key: KeyCode | str):
        if isinstance(key, KeyCode):
            return key

        keys = {k: v for k, v in cls.__dict__.items()
                if not k.startswith('_')}
        keys |= {None: 0x00, ' ': 0x2C}
        keys |= {chr(ord('a') + i): 0x04 + i for i in range(26)}
        keys |= {chr(ord('A') + i): 0x04 + i for i in range(26)}
        keys |= {c: 0x1E + i for i, c in enumerate('1234567890')}
        keys |= {c: 0x1A + i for i, c in enumerate('!@#$%^&*()')}
        keys |= {c: 0x2D + i for i, c in enumerate('-=[]\\')}
        keys |= {c: 0x2D + i for i, c in enumerate('_+{}|')}
        keys |= {c: 0x33 + i for i, c in enumerate(";'`,./")}
        keys |= {c: 0x33 + i for i, c in enumerate(':"~<>?')}

        return KeyCode(keys[key])

    NONE = KeyCode(0x00)
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
    NUMPAD_1 = KeyCode(0x59)
    NUMPAD_END = KeyCode(0x59)
    NUMPAD_2 = KeyCode(0x5A)
    NUMPAD_DOWN_ARROW = KeyCode(0x5A)
    NUMPAD_3 = KeyCode(0x5B)
    NUMPAD_PAGE_DOWN = KeyCode(0x5B)
    NUMPAD_4 = KeyCode(0x5C)
    NUMPAD_LEFT_ARROW = KeyCode(0x5C)
    NUMPAD_5 = KeyCode(0x5D)
    NUMPAD_6 = KeyCode(0x5E)
    NUMPAD_RIGHT_ARROW = KeyCode(0x5E)
    NUMPAD_7 = KeyCode(0x5F)
    NUMPAD_HOME = KeyCode(0x5F)
    NUMPAD_8 = KeyCode(0x60)
    NUMPAD_UP_ARROW = KeyCode(0x60)
    NUMPAD_9 = KeyCode(0x61)
    NUMPAD_PAGE_UP = KeyCode(0x61)
    NUMPAD_0 = KeyCode(0x62)
    NUMPAD_INSERT = KeyCode(0x62)
    NUMPAD_PERIOD = KeyCode(0x63)
    NUMPAD_DELETE = KeyCode(0x63)
    APPLICATION = KeyCode(0x65)


class KeyboardReport():
    pass


class Keyboard(KeyboardReport):
    pass
