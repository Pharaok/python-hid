"""https://www.usb.org/sites/default/files/hid1_11.pdf"""
from __future__ import annotations

from collections.abc import Iterable, Sequence
from math import ceil
from typing import Union, overload

from hid.helpers import flatten
from .item import *

_DT = Iterable[Union[BaseItem, '_DT']]  # type: ignore


class ReportDescriptor(Sequence[BaseItem]):
    def __init__(self, descriptor: Union[bytes, _DT]) -> None:
        if isinstance(descriptor, bytes):
            self._items = []
            i = 0
            while i < len(descriptor):
                x = BaseItem.from_bytes(descriptor[i:])
                self._items.append(x)
                i += len(x)
        else:
            self._items = flatten(descriptor, ignore=(BaseItem,))

        global_items: dict[int, int] = {}
        local_items: dict[int, int] = {}
        input_items = []
        for x in self._items:
            if not isinstance(x, BaseItem):
                raise TypeError

            if x.size == 0:
                continue
            data = int.from_bytes(x.data, 'little')
            if isinstance(x, BaseMainItem):
                if isinstance(x, Input):
                    input_items.append(global_items | local_items)
                local_items.clear()
            elif isinstance(x, BaseGlobalItem):
                global_items[x.PREFIX] = data
            elif isinstance(x, BaseLocalItem):
                local_items[x.PREFIX] = data

        input_bit_len = 0
        for y in input_items:
            input_bit_len += y[ReportSize.PREFIX] * y[ReportCount.PREFIX]
        self.input_size = ceil(input_bit_len / 8)

    @overload
    def __getitem__(self, i: int) -> BaseItem:
        ...

    @overload
    def __getitem__(self, s: slice) -> Sequence[BaseItem]:
        ...

    def __getitem__(self, x):  # type: ignore
        return self._items[x]

    def __len__(self) -> int:
        return len(self._items)

    def __bytes__(self) -> bytes:
        return bytes(flatten(self._items))

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._items!r})'


class ProtocolCode(IntEnum):
    NONE = 0
    KEYBOARD = auto()
    MOUSE = auto()


class SubclassCode(IntEnum):
    NONE = 0
    BOOT_INTERFACE = auto()
