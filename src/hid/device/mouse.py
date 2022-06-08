from __future__ import annotations

from ctypes import Structure, c_ubyte, c_byte
from math import floor
from time import sleep
from typing import Literal

from hid.report import ProtocolCode, SubclassCode, ReportDescriptor
from hid.report.item import *
from hid.report.usage import UsagePages
from . import HIDDevice
from ..gadget import Gadget


class MouseButton(IntEnum):
    LEFT = auto()
    MIDDLE = auto()
    RIGHT = auto()


class MouseReport(Structure):
    _fields_ = [('buttons', c_ubyte, 3),
                ('', c_ubyte, 5),
                ('x', c_byte),
                ('y', c_byte)]


class Mouse(HIDDevice):
    DESCRIPTOR = ReportDescriptor((
        UsagePage(UsagePages.GENERIC_DESKTOP),
        Usage(2),
        Collection(CollectionType.APPLICATION),
        (
            Usage(1),
            Collection(CollectionType.PHYSICAL),
            (
                UsagePage(UsagePages.BUTTON),
                UsageMinimum(1),
                UsageMaximum(3),
                LogicalMinimum(0),
                LogicalMaximum(1),
                ReportCount(3),
                ReportSize(1),
                Input(DataFlag.VARIABLE),

                ReportCount(1),
                ReportSize(5),
                Input(DataFlag.CONSTANT | DataFlag.VARIABLE),

                UsagePage(UsagePages.GENERIC_DESKTOP),
                Usage(0x30),
                Usage(0x31),
                LogicalMinimum(-127),
                LogicalMaximum(127),
                ReportSize(8),
                ReportCount(2),
                Input(DataFlag.VARIABLE | DataFlag.RELATIVE)
            ),
            EndCollection()
        ),
        EndCollection()
    ))
    PROTOCOL = ProtocolCode.MOUSE
    SUBCLASS = SubclassCode.BOOT_INTERFACE

    def __init__(self, gadget: Optional[Gadget] = None, frequency: int = 250):
        self.frequency = frequency
        self.buttons = 0
        self._x = 0
        self._y = 0
        super().__init__(gadget)

    def move(self, x: float = 0, y: float = 0, t: float = 0) -> Mouse:
        t = max(t, 1 / self.frequency)

        n = floor(t * self.frequency)

        if not (-127 <= x / n <= 127 and -127 <= y / n <= 127):
            raise ValueError

        report = MouseReport(self.buttons)
        for _ in range(n):
            self._x += x / n
            self._y += y / n

            report.x, report.y = floor(self._x), floor(self._y)
            self._x -= report.x
            self._y -= report.y

            self.send_report(report)
            sleep(1 / self.frequency)
        return self

    def click(self, button: int = MouseButton.LEFT, direction: Literal['up', 'down', 'both'] = 'both') -> Mouse:
        if direction in ['down', 'both']:
            self.buttons |= button
            self.send_report(MouseReport(self.buttons))
            sleep(1 / self.frequency)
        if direction in ['up', 'both']:
            self.buttons &= ~button
            self.send_report(MouseReport(self.buttons))
            sleep(1 / self.frequency)
        else:
            raise ValueError
        return self

    def __enter__(self) -> Mouse:
        return super().__enter__()            