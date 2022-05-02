from __future__ import annotations

from enum import IntEnum, IntFlag, auto
from math import ceil
from typing import Literal, SupportsIndex
from collections.abc import Iterable


def int_to_min_bytes(n: int, byteorder: Literal['little', 'big'] = 'little') -> bytes:
    l = max(1, ceil(n.bit_length() / 8))
    return n.to_bytes(l, byteorder)



class UsagePages(IntEnum):
    GENERIC_DESKTOP = auto()
    SIMULATION_CONTROLS = auto()
    VR_CONTROLS = auto()
    SPORT_CONTROLS = auto()
    GAME_CONTROLS = auto()
    GENERIC_DEVICE_CONTROLS = auto()
    KEYBOARD = auto()
    KEYPAD = KEYBOARD
    LED = auto()
    BUTTON = auto()
    ORDINAL = auto()
    TELEPHONY = auto()
    CONSUMER = auto()
    DIGITIZERS = auto()
    HAPTICS = auto()
    PHYISICAL_INPUT_DEVICE = auto()
    UNICODE = auto()
    EYE_AND_HEAD_TRACKERS = 0x12
    AUXILIARY_DISPLAY = 0x14
    SENSORS = 0x20
    MEDICAL_INSTRUMENT = 0x40
    BRAILLE_DISPLAY = auto()
    LIGHTING_ANDILLUMINATION = 0x59
    MONITOR = 0x80
    MONITOR_ENUMERATED = auto()
    VESA_VIRTUAL_CONTROLS = auto()
    POWER = 0x84
    BATTERY_SYSTEM = auto()
    BARCODE_SCANNER = 0x8C
    SCALES = auto()
    MAGNETIC_STRIPE_READER = auto()
    CAMERA_CONTROL = 0x90
    ARCADE = auto()
    GAMING_DEVICE = auto()



class BaseItem(bytes):
    PREFIX: int = NotImplemented

    def __new__(cls, data):
        if cls.PREFIX is NotImplemented:
            raise NotImplementedError

        if isinstance(data, int):
            d = int_to_min_bytes(data)
        else:
            d = bytes(data)
        l = len(d)
        if l.bit_length() > 2:
            raise OverflowError("Data is too large.")

        b = bytes([cls.PREFIX | l]) + d
        return super().__new__(cls, b)

    def __init_subclass__(cls) -> None:
        if cls.PREFIX is NotImplemented:
            return
        if cls.PREFIX.bit_length() > 8:
            raise ValueError("Prefix must fit in 1 byte.")
        if cls.PREFIX & 0b11 != 0:
            raise ValueError("Last 2 bits in the prefix are reserved for size.")


class BaseFlagItem(BaseItem):
    def __new__(cls, /, *flags: int):
        n = 0
        for f in flags:
            n |= f
        b = int_to_min_bytes(n)
        return super().__new__(cls, b)
