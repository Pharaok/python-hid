from __future__ import annotations

from typing import Optional


class KeyboardReport():
    def __init__(self, x: Optional[KeyboardReport] = None, /) -> None:
        self.modifiers = 0
        self.keys = []
        if x:
            self.modifiers = x.modifiers
            self.keys = x.keys


class Keyboard(KeyboardReport):
    pass
