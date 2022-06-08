from __future__ import annotations

import os
import platform
from types import TracebackType
from typing import Mapping, Optional, Union, Type, Literal, Iterable

from typing_extensions import Self

from hid.devices.hid_device import HIDDevice
from hid.helpers import Directory, SymLink

_KT = str
_VT = Union[str, bytes, 'SymLink', 'Directory']
_GT = Mapping[_KT, Union[_VT, '_GT']]  # type: ignore


class Gadget:
    def __init__(self,
                 functions: Iterable[HIDDevice],
                 vendor_id: int = 0x1d6b,
                 product_id: int = 0x0104,
                 serial_number: str = '1234567890',
                 manufacturer: str = 'Pharaok',
                 product_name: str = 'Pi02',
                 udc: Optional[str] = None,
                 path: str = '/sys/kernel/config/usb_gadget/',
                 name: str = 'hidpy') -> None:
        if platform.system() != 'Linux':
            raise Exception(f'Unsupported platform: {platform.system()}. Please use linux.')

        self.configfs = Directory(f'{path}/hidpy', {
            'idVendor': f'0x{vendor_id:04x}',
            'idProduct': f'0x{product_id:04x}',
            'bcdDevice': '0x0100',
            'bcdUSB': '0x0200',
            'strings': {
                '0x409': {
                    'serialnumber': serial_number,
                    'manufacturer': manufacturer,
                    'product': product_name
                }
            },
            'configs': {
                'c.1': {
                    'strings': {
                        '0x409': {
                            'configuration': 'Config 1'
                        }
                    },
                    'MaxPower': '250'
                }
            }
        })
        self.name = name

        if udc is not None:
            self.udc = udc
        else:
            try:
                self.udc = os.listdir('/sys/class/udc')[0]
            except FileNotFoundError:
                pass

        self._names = []

        for f in functions:
            self.add_function(f)
            self._names.append(f.name)
        self.enabled = True

    def __dir__(self) -> Iterable[str]:
        return list(super().__dir__()) + self._names

    def __enter__(self) -> Self:
        return self

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]) -> Literal[False]:
        self.close()
        return False

    def close(self) -> None:
        self.enabled = False

        self.configfs.pop('configs/c.1/strings/0x409')

        for f in self.functions:
            self.configfs.pop(f'configs/c.1/{f}')

        self.configfs.pop('configs/c.1')

        for f in self.functions:
            self.configfs.pop(f'functions/{f}')

        self.configfs.pop('strings/0x409')

        os.rmdir(self.configfs.path)

    @property
    def enabled(self) -> bool:
        udc = self.configfs['UDC']
        if not isinstance(udc, str):
            raise TypeError
        return bool(udc.strip())

    @enabled.setter
    def enabled(self, b: bool) -> None:
        if b and not self.enabled:
            if self.udc is None:
                raise Exception('No UDC chosen.')
            self.configfs['UDC'] = self.udc
        else:
            self.configfs['UDC'] = ''

    @property
    def udc(self) -> Optional[str]:
        if not hasattr(self, '_udc'):
            return None
        return self._udc

    @udc.setter
    def udc(self, udc: str) -> None:
        if udc not in os.listdir('/sys/class/udc'):
            raise ValueError(f"'{self.udc}' is not a valid UDC. Please choose a UDC from /sys/class/udc.")
        self._udc = udc

    @property
    def functions(self) -> Directory:
        f = self.configfs['functions']
        if not isinstance(f, Directory):
            raise Exception("'functions' is not a directory.")
        return f

    def add_function(self, function: HIDDevice) -> None:
        name = f'hid.{function.name}'

        self.configfs[f'functions/{name}'] = {
            'protocol': f'{function.PROTOCOL}',
            'subclass': f'{function.SUBCLASS}',
            'report_length': f'{function.DESCRIPTOR.input_len}',
            'report_desc': function.DESCRIPTOR
        }
        self.configfs[f'configs/c.1/{name}'] = SymLink(self.configfs[f'functions/{name}'].path)

        dev = self.configfs[f'functions/{name}/dev']
        if not isinstance(dev, str):
            raise TypeError
        function.dev = f"/dev/hidg{dev.split(':')[1].strip()}"
        if hasattr(self, function.name):
            raise ValueError(f"Attribute '{function.name}' already exists.")
        setattr(self, function.name, function)
