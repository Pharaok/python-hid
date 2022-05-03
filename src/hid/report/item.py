from __future__ import annotations
from collections.abc import Iterable
from enum import IntEnum, IntFlag, auto
from typing import Optional

from hid.helpers import flatten, ConvertibleToBytes, int_to_min_bytes, convert_to_bytes


def item_from_bytes(b: bytes) -> BaseItem:
    prefix = int(b[0])
    for k, v in globals().items():
        if k.startswith('_'):
            continue
        if isinstance(v, type):
            if issubclass(v, BaseItem):
                if v.PREFIX is NotImplemented:
                    continue
                if prefix & 0b11111100 == v.PREFIX:
                    print(v)
                    return v(b[1:])


class DataFlag(IntFlag):
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


class CollectionType(IntEnum):
    PHYSICAL = 0x00
    APPLICATION = auto()
    LOGICAL = auto()
    REPORT = auto()
    NAMED_ARRAY = auto()
    USAGE_SWITCH = auto()
    USAGE_MODIFIER = auto()


class BaseItem(bytes):
    PREFIX: int = NotImplemented
    _SIZE_MASK = 0b00000011

    def __new__(cls, prefix_data: Optional[ConvertibleToBytes] = None) -> BaseItem:
        if cls.PREFIX is NotImplemented:
            raise NotImplementedError
        b = bytearray([cls.PREFIX])
        if prefix_data is not None:
            data = convert_to_bytes(prefix_data)
            data_len = len(data)
            if data_len.bit_length() > cls._SIZE_MASK.bit_length():
                raise OverflowError('Data is too large.')
            b[0] |= data_len
            b += data
        return super().__new__(cls, b)

    def __init_subclass__(cls) -> None:
        if cls.PREFIX is NotImplemented:
            return
        if cls.PREFIX.bit_length() > 8:
            raise ValueError('Prefix must fit in 1 byte.')
        if cls.PREFIX & cls._SIZE_MASK != 0:
            raise ValueError("Prefix can't overlap with size mask.")

    def __repr__(self) -> str:
        return f'{self.__class__.__qualname__}({self[1:].__repr__()})'


class BaseFlagItem(BaseItem):
    def __new__(cls, *flags: int) -> BaseFlagItem:
        n = 0
        for f in flags:
            n |= f
        b = int_to_min_bytes(n)
        return super().__new__(cls, b)


class BaseMainItem(BaseItem):
    pass


class Input(BaseFlagItem, BaseMainItem):
    PREFIX = 0b10000000


class Output(BaseFlagItem, BaseMainItem):
    PREFIX = 0b10010000


class Feature(BaseFlagItem, BaseMainItem):
    PREFIX = 0b10110000


class Collection(BaseMainItem):
    PREFIX = 0b10100000

    def __new__(cls,
                prefix_data: Optional[ConvertibleToBytes],
                content: Optional[Iterable[BaseItem]] = None) -> Collection:
        prefix = super().__new__(cls, prefix_data)
        b = bytes(prefix)
        if content:
            b += bytes(flatten(content))
            b += bytes(CollectionEnd())
        return bytes.__new__(cls, b)

    def __init__(self,
                 prefix_data: Optional[ConvertibleToBytes],
                 content: Optional[Iterable[BaseItem]] = None) -> None:
        if content:
            prefix = self.__class__(prefix_data)
            self.items = (prefix, *flatten(content, ignore=(BaseItem,)), CollectionEnd())


class CollectionEnd(BaseMainItem):
    PREFIX = 0b11000000

    def __new__(cls) -> CollectionEnd:
        return super().__new__(cls)


class BaseGlobalItem(BaseItem):
    pass


class UsagePage(BaseGlobalItem):
    PREFIX = 0b00000100


class LogicalMinimum(BaseGlobalItem):
    PREFIX = 0b00010100


class LogicalMaximum(BaseGlobalItem):
    PREFIX = 0b00100100


class PhysicalMinimum(BaseGlobalItem):
    PREFIX = 0b00110100


class PhysicalMaximum(BaseGlobalItem):
    PREFIX = 0b01000100


class UnitExponent(BaseGlobalItem):
    PREFIX = 0b01010100


class Unit(BaseGlobalItem):
    PREFIX = 0b01110100


class ReportSize(BaseGlobalItem):
    PREFIX = 0b01110100


class ReportID(BaseGlobalItem):
    PREFIX = 0b10000100


class ReportCount(BaseGlobalItem):
    PREFIX = 0b10010100


class Push(BaseGlobalItem):
    PREFIX = 0b10100100


class Pop(BaseGlobalItem):
    PREFIX = 0b10110100


class BaseLocalItem(BaseItem):
    pass


class Usage(BaseLocalItem):
    PREFIX = 0b00001000


class UsageMinimum(BaseLocalItem):
    PREFIX = 0b00011000


class UsageMaximum(BaseLocalItem):
    PREFIX = 0b00101000


class DesignatorIndex(BaseLocalItem):
    PREFIX = 0b00111000


class DesignatorMinimum(BaseLocalItem):
    PREFIX = 0b01001000


class DesignatorMaximum(BaseLocalItem):
    PREFIX = 0b01011000


class StringIndex(BaseLocalItem):
    PREFIX = 0b01111000


class StringMinimum(BaseLocalItem):
    PREFIX = 0b10001000


class StringMaximum(BaseLocalItem):
    PREFIX = 0b10011000


class Delimiter(BaseLocalItem):
    PREFIX = 0b10101000
