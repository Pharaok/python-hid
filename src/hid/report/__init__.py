"""https://www.usb.org/sites/default/files/hid1_11.pdf"""
from __future__ import annotations

from collections.abc import Iterable
from math import ceil
from typing import Union, Generator, SupportsBytes

from hid.helpers import flatten
from .item import *

_DT = Iterable[Union[BaseItem, '_DT']]  # type: ignore


class ReportDescriptor(bytes):
    def __new__(cls, descriptor: Union[bytes, _DT]) -> ReportDescriptor:
        b = flatten(descriptor)
        return super().__new__(cls, b)

    def __init__(self, descriptor: Union[bytes, _DT]) -> None:
        global_items: dict[int, int] = {}
        local_items: dict[int, int] = {}
        input_items = []
        output_items = []

        for x in self.items():
            if not isinstance(x, BaseItem):
                raise TypeError

            if x.size == 0:
                continue
            data = int.from_bytes(x.data, 'little')
            if isinstance(x, BaseMainItem):
                if isinstance(x, Input):
                    input_items.append(global_items | local_items)
                elif isinstance(x, Output):
                    output_items.append(global_items | local_items)
                local_items.clear()
            elif isinstance(x, BaseGlobalItem):
                global_items[x.PREFIX] = data
            elif isinstance(x, BaseLocalItem):
                local_items[x.PREFIX] = data

        input_bit_len = 0
        for y in input_items:
            input_bit_len += y[ReportSize.PREFIX] * y[ReportCount.PREFIX]
        self.input_len = ceil(input_bit_len / 8)
        output_bit_len = 0
        for y in output_items:
            output_bit_len += y[ReportSize.PREFIX] * y[ReportCount.PREFIX]
        self.output_len = ceil(output_bit_len / 8)

    def items(self) -> Generator[BaseItem, None, None]:
        i = 0
        while i < len(self):
            x = BaseItem.from_bytes(self[i:])
            yield x
            i += len(x)

    def validate_input_report(self, report: SupportsBytes | Iterable[SupportsIndex]) -> bool:
        report = bytes(report)
        if not len(report) == self.input_len:
            return False
        return True


class ProtocolCode(IntEnum):
    NONE = 0
    KEYBOARD = auto()
    MOUSE = auto()


class SubclassCode(IntEnum):
    NONE = 0
    BOOT_INTERFACE = auto()
