from __future__ import annotations

import os

from hid.report import *


class HIDDevice:
    DESCRIPTOR: ReportDescriptor = NotImplemented
    PROTOCOL = ProtocolCode.NONE
    SUBCLASS = SubclassCode.NONE

    def __init__(self, name: str) -> None:
        self.name = name
        self.dev = NotImplemented
        # threading.Thread(target=self._listener).start()

    def send_report(self, report: SupportsBytes | Iterable[SupportsIndex]) -> None:
        report = bytes(report)
        if self.dev is NotImplemented:
            raise NotImplementedError
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
