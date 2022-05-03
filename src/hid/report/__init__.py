from __future__ import annotations
from typing import Optional

from hid.helpers import int_to_min_bytes, convert_to_bytes, ConvertibleToBytes


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


class BaseFlagItem(BaseItem):
    def __new__(cls, *flags: int) -> BaseFlagItem:
        n = 0
        for f in flags:
            n |= f
        b = int_to_min_bytes(n)
        return super().__new__(cls, b)


