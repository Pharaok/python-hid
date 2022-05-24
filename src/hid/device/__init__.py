from __future__ import annotations

import threading
from collections.abc import Iterable
from types import TracebackType
from typing import Optional, SupportsIndex, SupportsBytes, Type, Literal, TypeVar

from hid.gadget import Gadget
from hid.report import ReportDescriptor, ProtocolCode, SubclassCode

_T_HIDDevice = TypeVar('_T_HIDDevice', bound='HIDDevice')

class HIDDevice:
    DESCRIPTOR: ReportDescriptor = NotImplemented
    PROTOCOL = ProtocolCode.NONE
    SUBCLASS = SubclassCode.NONE

    def __init__(self, gadget: Optional[Gadget] = None) -> None:
        if gadget is None:
            gadget = Gadget()
        self.gadget = gadget

        self.function = gadget.add_function({
            'protocol': f'{ProtocolCode.KEYBOARD}',
            'subclass': f'{SubclassCode.BOOT_INTERFACE}',
            'report_length': f'{self.DESCRIPTOR.input_len}',
            'report_desc': self.DESCRIPTOR
        })
        self.gadget.enabled = True

        dev = self.function['dev']
        if not isinstance(dev, str):
            raise TypeError
        self.dev = f"/dev/hidg{dev.split(':')[1].strip()}"

        threading.Thread(target=self._listener).start()

    def send_report(self, report: SupportsBytes | Iterable[SupportsIndex]) -> None:
        report = bytes(report)
        if not self.gadget.enabled:
            raise Exception
        if not self.DESCRIPTOR.validate_input_report(report):
            raise ValueError
        with open(self.dev, "wb") as f:
            f.write(report)

    def _listener(self) -> None:
        while True:
            with open(self.dev, 'rb') as fd:
                self.output = fd.read(self.DESCRIPTOR.output_len)

    def __enter__(self) -> _T_HIDDevice:
        return self

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> Literal[False]:
        return False
