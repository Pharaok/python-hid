"""https://www.usb.org/sites/default/files/hid1_11.pdf"""
from __future__ import annotations

from enum import IntEnum, auto


class ProtocolCode(IntEnum):
    NONE = 0
    KEYBOARD = auto()
    MOUSE = auto()


class SubclassCode(IntEnum):
    NONE = 0
    BOOT_INTERFACE = auto()
