from __future__ import annotations

from enum import IntEnum, IntFlag, auto
from typing import Optional, SupportsIndex, TypeVar, Type

from hid.helpers import ConvertibleToBytes, convert_to_bytes, deep_subclasses


class CollectionType(IntEnum):
    PHYSICAL = 0x00
    APPLICATION = auto()
    LOGICAL = auto()
    REPORT = auto()
    NAMED_ARRAY = auto()
    USAGE_SWITCH = auto()
    USAGE_MODIFIER = auto()


class DataFlag(IntFlag):
    CONSTANT = auto()
    VARIABLE = auto()
    RELATIVE = auto()
    WRAP = auto()
    NON_LINEAR = auto()
    NO_PREFERRED = auto()
    NULL_STATE = auto()
    VOLATILE = auto()
    BUFFER = auto()


_BT = TypeVar('_BT', bound='BaseItem')
class BaseItem(bytes):
    PREFIX: int = NotImplemented
    _PREFIX_MASK = 0b11111100
    _SIZE_MASK = 0b00000011
    _SIZES = (0, 1, 2, 4)

    def __new__(cls: Type[_BT], prefix_data: Optional[ConvertibleToBytes] = None) -> _BT:
        if cls.PREFIX is NotImplemented:
            raise NotImplementedError

        b = bytearray([cls.PREFIX])
        if prefix_data is not None:
            data = convert_to_bytes(prefix_data)
            data_len = len(data)
            if data_len.bit_length() > max(cls._SIZES):
                raise OverflowError(f'Data is too large. Maximum size: {max(cls._SIZES)}')

            index = min([x for x in enumerate(cls._SIZES) if x[1] >= data_len], key=lambda x: x[1])[0]
            b[0] |= index
            b += data

        return super().__new__(cls, b)

    def __init_subclass__(cls) -> None:
        if cls.PREFIX is NotImplemented:
            return
        for sc in deep_subclasses(BaseItem):
            if sc is cls:
                continue
            if sc.PREFIX == cls.PREFIX:
                raise ValueError(f"Prefix can't be the same as another subclass of BaseItem: {sc.__name__}")
        if cls.PREFIX.bit_length() > 8:
            raise ValueError('Prefix must fit in 1 byte.')
        inverted_prefix_mask = ((1 << 8) - 1) ^ cls._PREFIX_MASK
        if cls.PREFIX & inverted_prefix_mask != 0:
            raise ValueError("Prefix can't overlap with size mask.")

    @classmethod
    def from_bytes(cls, b: bytes) -> BaseItem:
        size = b[0] & cls._SIZE_MASK
        for c in filter(lambda d: d.PREFIX is not NotImplemented, deep_subclasses(cls)):
            inverted_size_mask = ((1 << 8) - 1) ^ cls._SIZE_MASK
            if b[0] & inverted_size_mask == c.PREFIX:
                return c(b[1:1 + size])
        raise ValueError

    def __repr__(self) -> str:
        return f'{self.__class__.__qualname__}({self.data!r})'

    @property
    def size(self) -> int:
        return self._SIZES[self[0] & self._SIZE_MASK]

    @property
    def data(self) -> bytes:
        return bytes(self[1:1 + self.size])


_FT = TypeVar('_FT', bound='BaseFlagItem')
class BaseFlagItem(BaseItem):
    def __new__(cls: Type[_FT], *flags: SupportsIndex) -> _FT:
        if not all([isinstance(x, SupportsIndex) for x in flags]):
            return super().__new__(cls, *flags)
        n = 0
        for f in flags:
            n |= int(f)
        return super().__new__(cls, n)


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


class EndCollection(BaseMainItem):
    PREFIX = 0b11000000

    def __new__(cls, prefix_data: Optional[ConvertibleToBytes] = None) -> EndCollection:
        if prefix_data:
            raise ValueError
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
    PREFIX = 0b01100100


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
