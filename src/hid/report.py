from __future__ import annotations

from abc import ABC, abstractmethod
from ctypes import Structure
from enum import IntEnum, IntFlag, auto
from math import ceil
from typing import Optional, SupportsBytes


class DataFlags(IntFlag):
    DATA = 0x00
    ARRAY = 0x00
    ABSOLUTE = 0x00
    NO_WRAP = 0x00
    LINEAR = 0x00
    PREFERRED_STATE = 0x00
    NO_NULL_POSITION = 0x00
    NON_VOLATILE = 0x00
    BIT_FIELD = 0x00
    CONSTANT = auto()
    VARIABLE = auto()
    RELATIVE = auto()
    WRAP = auto()
    NON_LINEAR = auto()
    NO_PREFERRED = auto()
    NULL_STATE = auto()
    VOLATILE = auto()
    BUFFER = auto()


class MainItemBase(ABC, bytes):
    @property
    @abstractmethod
    def PREFIX(self) -> int: ...

    def __new__(cls, data: SupportsBytes, content: Optional[SupportsBytes] = None):
        l = len(data)
        if l.bit_length() > 2:
            raise OverflowError("Data is too large.")

        b = bytes([cls.PREFIX | l]) + bytes(data)
        if content is not None:
            b += bytes(content)
        if hasattr(cls, 'POSTFIX'):
            b += bytes([cls.POSTFIX])

        return super().__new__(cls, b)

    def __init_subclass__(cls) -> None:
        if isinstance(cls.PREFIX, property):
            return
        if cls.PREFIX & 0b11 != 0:
            raise ValueError("Last 2 bits in the prefix are reserved for size.")


class FlagItemBase(MainItemBase):
    def __new__(cls, /, *flags: int):
        n = 0
        for f in flags:
            n = f
        l = max(1, ceil(n.bit_length() / 8))
        b = n.to_bytes(l, 'little')
        return super().__new__(cls, b)


class Input(FlagItemBase):
    PREFIX = 0b10000000


class Output(FlagItemBase):
    PREFIX = 0b10010000


class Feature(FlagItemBase):
    PREFIX = 0b10110000


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
