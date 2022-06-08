from __future__ import annotations

import os
import platform
from collections.abc import Sequence
from types import TracebackType
from typing import Mapping, Optional, Union, Type, Literal

from typing_extensions import Self

from hid.helpers import Directory, SymLink

_KT = str
_VT = Union[str, bytes, 'SymLink', 'Directory']
_GT = Mapping[_KT, Union[_VT, '_GT']]  # type: ignore


class Gadget:
    CONFIGFS = {
        'idVendor': '0x1d6b',
        'idProduct': '0x0104',
        'bcdDevice': '0x0100',
        'bcdUSB': '0x0200',
        'UDC': '',
        'strings': {
            '0x409': {
                'serialnumber': '1234567890',
                'manufacturer': 'Pharaok',
                'product': 'Pi02'
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
    }

    def __init__(self,
                 path: str = '/sys/kernel/config/usb_gadget/',
                 name: str = 'hidpy',
                 configfs: Optional[_GT] = None,
                 udc: Optional[str] = None,
                 functions: Optional[Sequence[_GT]] = None) -> None:
        if platform.system() != 'Linux':
            raise Exception(f'Unsupported platform: {platform.system()}. Please use linux.')

        self.configfs = Directory(f'{path}/{name}', self.CONFIGFS or configfs)
        self.name = name

        self._function_count = 0

        if functions is None:
            functions = []
        for f in functions:
            self.add_function(f)

        if udc is not None:
            self.udc = udc
        else:
            try:
                self.udc = os.listdir('/sys/class/udc')[0]
            except FileNotFoundError:
                pass

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

    def add_function(self, function: _GT, name: str = 'hid') -> Directory:
        n = f'{name}.usb{self._function_count}'
        self._function_count += 1

        self.configfs[f'functions/{n}'] = function
        f = self.configfs[f'functions/{n}']
        if not isinstance(f, Directory):
            raise TypeError
        self.configfs[f'configs/c.1/{n}'] = SymLink(f.path)
        return f
