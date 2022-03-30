from __future__ import annotations

from typing import Optional, Sequence


class KeyCode():
    def __class_getitem__(cls, key: str):
        if not isinstance(key, str):
            raise TypeError
        if len(key) != 1:
            raise ValueError

        _chars = {' ': 0x2C}
        _chars |= {chr(ord('a') + i): 0x04 + i for i in range(26)}
        _chars |= {chr(ord('A') + i): 0x04 + i for i in range(26)}
        _chars |= {c: 0x1E + i for i, c in enumerate('1234567890')}
        _chars |= {c: 0x1A + i for i, c in enumerate('!@#$%^&*()')}
        _chars |= {c: 0x2D + i for i, c in enumerate('-=[]\\')}
        _chars |= {c: 0x2D + i for i, c in enumerate('_+{}|')}
        _chars |= {c: 0x33 + i for i, c in enumerate(";'`,./")}
        _chars |= {c: 0x33 + i for i, c in enumerate(':"~<>?')}

        return _chars[key]

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
    NUMPAD_1 = 0x59
    NUMPAD_END = 0x59
    NUMPAD_2 = 0x5A
    NUMPAD_DOWN_ARROW = 0x5A
    NUMPAD_3 = 0x5B
    NUMPAD_PAGE_DOWN = 0x5B
    NUMPAD_4 = 0x5C
    NUMPAD_LEFT_ARROW = 0x5C
    NUMPAD_5 = 0x5D
    NUMPAD_6 = 0x5E
    NUMPAD_RIGHT_ARROW = 0x5E
    NUMPAD_7 = 0x5F
    NUMPAD_HOME = 0x5F
    NUMPAD_8 = 0x60
    NUMPAD_UP_ARROW = 0x60
    NUMPAD_9 = 0x61
    NUMPAD_PAGE_UP = 0x61
    NUMPAD_0 = 0x62
    NUMPAD_INSERT = 0x62
    NUMPAD_PERIOD = 0x63
    NUMPAD_DELETE = 0x63
    APPLICATION = 0x65


class KeyList():
    def __init__(self, keys: Sequence[KeyCode] = [], /) -> None:
        self._keys = [0] * 6
        for i in range(len(keys)):
            self._keys[i] = keys[i]
        self._keys = keys

    def press(self, key: int) -> None:
        self


class KeyboardReport():
    def __init__(self, x: Optional[KeyboardReport] = None, /) -> None:
        self.modifiers = 0
        self.keys = []
        if x:
            self.modifiers = x.modifiers
            self.keys = x.keys


class Keyboard(KeyboardReport):
    pass
