from __future__ import annotations

import os
import threading
from collections.abc import Iterable
from types import TracebackType
from typing import Optional, SupportsIndex, SupportsBytes, Type, Literal

from typing_extensions import Self

from hid.gadget import Gadget
from hid.report import ReportDescriptor, ProtocolCode, SubclassCode


class HIDDevice:
    DESCRIPTOR: ReportDescriptor = NotImplemented
    PROTOCOL = ProtocolCode.NONE
    SUBCLASS = SubclassCode.NONE

    def __init__(self, gadget: Optional[Gadget] = None) -> None:
        created_gadget = False
        if gadget is None:
            gadget = Gadget()
            created_gadget = True
        self.gadget = gadget

        self.function = self.gadget.add_function({
            'protocol': f'{ProtocolCode.KEYBOARD}',
            'subclass': f'{SubclassCode.BOOT_INTERFACE}',
            'report_length': f'{self.DESCRIPTOR.input_len}',
            'report_desc': self.DESCRIPTOR
        })
        if created_gadget:
            self.gadget.enabled = True

        dev = self.function['dev']
        if not isinstance(dev, str):
            raise TypeError
        self.dev = f"/dev/hidg{dev.split(':')[1].strip()}"

        threading.Thread(target=self._listener).start()

    def send_report(self, report: SupportsBytes | Iterable[SupportsIndex]) -> None:
        report = bytes(report)
        if not os.path.exists(self.dev):
            raise FileNotFoundError
        if not self.DESCRIPTOR.validate_input_report(report):
            raise ValueError
        with open(self.dev, 'wb') as fd:
            fd.write(report)

    def _listener(self) -> None:
        while os.path.exists(self.dev):
            with open(self.dev, 'rb') as fd:
                self.output = fd.read(self.DESCRIPTOR.output_len)

    def __enter__(self) -> Self:
        self.gadget.enabled = True
        return self

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> Literal[False]:
        self.gadget.close()
        return False
