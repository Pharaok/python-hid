from __future__ import annotations

from abc import ABC, abstractmethod
from ctypes import Structure
from enum import IntEnum, IntFlag, auto
from math import ceil
from typing import Optional, SupportsBytes, Literal, SupportsInt


def int_to_min_bytes(n: int, byteorder: Literal['little', 'big'] = 'little') -> bytes:
    l = max(1, ceil(n.bit_length() / 8))
    return n.to_bytes(l, byteorder)


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


class ItemBase(ABC, bytes):
    @property
    @abstractmethod
    def PREFIX(self) -> int: ...

    def __new__(cls, data: SupportsBytes | int, content: Optional[SupportsBytes] = None):
        if isinstance(data, int):
            data = int_to_min_bytes(data)

        l = len(bytes(data))
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
        if cls.PREFIX.bit_length() > 8 or cls.PREFIX & 0b11 != 0:
            raise ValueError("Last 2 bits in the prefix are reserved for size.")


class FlagItemBase(ItemBase):
    def __new__(cls, /, *flags: int):
        n = 0
        for f in flags:
            n = f
        b = int_to_min_bytes(n)
        return super().__new__(cls, b)


# Main items


class Input(FlagItemBase):
    PREFIX = 0b10000000


class Output(FlagItemBase):
    PREFIX = 0b10010000


class Feature(FlagItemBase):
    PREFIX = 0b10110000


# Global items


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


class UsagePage(ItemBase):
    PREFIX = 0b00000100


class LogicalMinimum(ItemBase):
    PREFIX = 0b00010100


class LogicalMaximum(ItemBase):
    PREFIX = 0b00100100


class PhysicalMinimum(ItemBase):
    PREFIX = 0b00110100


class PhysicalMaximum(ItemBase):
    PREFIX = 0b01000100


class UnitExponent(ItemBase):
    PREFIX = 0b01010100


class Unit(ItemBase):
    PREFIX = 0b01110100


class ReportID(ItemBase):
    PREFIX = 0b10000100


class ReportCount(ItemBase):
    PREFIX = 0b10010100


class Push(ItemBase):
    PREFIX = 0b10100100


class Pop(ItemBase):
    PREFIX = 0b10110100


# Local items


class Usage(ItemBase):
    PREFIX = 0b00001000


class UsageMinimum(ItemBase):
    PREFIX = 0b00011000


class UsageMaximum(ItemBase):
    PREFIX = 0b00101000


class DesignatorIndex(ItemBase):
    PREFIX = 0b00111000


class DesignatorMinimum(ItemBase):
    PREFIX = 0b01001000


class DesignatorMaximum(ItemBase):
    PREFIX = 0b01011000


class StringIndex(ItemBase):
    PREFIX = 0b01111000


class StringMinimum(ItemBase):
    PREFIX = 0b10001000


class StringMaximum(ItemBase):
    PREFIX = 0b10011000


class Delimitre(ItemBase):
    PREFIX = 0b10101000
