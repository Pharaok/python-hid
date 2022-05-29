from __future__ import annotations

from enum import IntEnum, IntFlag, auto
from math import ceil
from typing import Optional, TypeVar, Type, Any, SupportsIndex, SupportsBytes, Iterable

from hid.helpers import ConvertibleToBytes, deep_subclasses


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
    SIGNED = False
    _PREFIX_MASK = 0b11111100
    _SIZE_MASK = 0b00000011
    _SIZES = (0, 1, 2, 4)

    def __new__(cls: Type[_BT], prefix_data: Optional[ConvertibleToBytes] = None) -> _BT:
        if cls.PREFIX is NotImplemented:
            raise NotImplementedError

        x = bytearray([cls.PREFIX])
        if prefix_data is not None:
            if isinstance(prefix_data, (Iterable, SupportsBytes)):
                b = bytes(prefix_data)
                if len(b) not in cls._SIZES:
                    raise ValueError
            elif isinstance(prefix_data, SupportsIndex):
                n = int(prefix_data)
                if n == 0: # bit_length() of 0 is 0
                    size = 1
                else:
                    # sign bit (not included in bit_length)
                    #                                   vvv
                    size = ceil((n.bit_length() + int(cls.SIGNED)) / 8)
                min_size = min([x for x in cls._SIZES if x >= size])
                b = n.to_bytes(min_size, 'little', signed=cls.SIGNED)
            else:
                raise TypeError

            x[0] |= cls._SIZES.index(len(b))
            x += b

        return super().__new__(cls, x)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
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
        for c in filter(lambda x: x.PREFIX is not NotImplemented, deep_subclasses(cls)):
            if b[0] & cls._PREFIX_MASK == c.PREFIX:
                size = cls._SIZES[b[0] & cls._SIZE_MASK]
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


class BaseMainItem(BaseItem):
    pass


class Input(BaseMainItem):
    PREFIX = 0b10000000

    def __new__(cls, prefix_data: Optional[ConvertibleToBytes] = None):
        if prefix_data is None:
            prefix_data = bytes([0])
        return super().__new__(cls, prefix_data)


class Output(BaseMainItem):
    PREFIX = 0b10010000

    def __new__(cls, prefix_data: Optional[ConvertibleToBytes] = None):
        if prefix_data is None:
            prefix_data = bytes([0])
        return super().__new__(cls,  prefix_data)


class Feature(BaseMainItem):
    PREFIX = 0b10110000

    def __new__(cls, prefix_data: Optional[ConvertibleToBytes] = None):
        if prefix_data is None:
            prefix_data = bytes([0])
        return super().__new__(cls, prefix_data)


class Collection(BaseMainItem):
    PREFIX = 0b10100000

    def __new__(cls, prefix_data: Optional[ConvertibleToBytes] = None):
        if prefix_data is None:
            prefix_data = bytes([0])
        return super().__new__(cls, prefix_data)


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
    SIGNED = True


class LogicalMaximum(BaseGlobalItem):
    PREFIX = 0b00100100
    SIGNED = True


class PhysicalMinimum(BaseGlobalItem):
    PREFIX = 0b00110100
    SIGNED = True


class PhysicalMaximum(BaseGlobalItem):
    PREFIX = 0b01000100
    SIGNED = True


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
