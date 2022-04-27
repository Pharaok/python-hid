from __future__ import annotations

import os
import platform
from collections.abc import Iterator, MutableMapping, Sequence
from dataclasses import dataclass
import shutil
from typing import Mapping, Optional, Union
from typing_extensions import Self

_KT = str
_VT = Union[str, bytes, 'SymLink', 'Directory']
_GT = Mapping[_KT, Union[_VT, '_GT']]  # type: ignore


@dataclass
class SymLink:
    src: str


class Directory(MutableMapping[_KT, _VT]):
    def __init__(self, path: str, m: Optional[_GT] = None) -> None:
        self.path = path
        os.makedirs(self.path, exist_ok=True)

        if m is None:
            m = {}
        for k, v in m.items():
            self[k] = v

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, path: str) -> str:
        p = os.path.abspath(path)
        if hasattr(self, '_path'):
            shutil.copytree(self._path, p, dirs_exist_ok=True)
            shutil.rmtree(self._path)
        self._path = p

    def __getitem__(self, k: _KT) -> _VT:
        p = os.path.abspath(self.path + os.sep + k)
        if os.path.isfile(p):
            try:
                with open(p, 'rt') as f:
                    return f.read()
            except UnicodeDecodeError:
                with open(p, 'rb') as f:
                    return f.read()
        elif os.path.isdir(p):
            return Directory(p)
        raise KeyError("Path doesn't exist.")

    def __setitem__(self, k: _KT, v: _VT | _GT) -> None:
        p = os.path.abspath(self.path + os.sep + k)

        if not p.startswith(self.path):
            raise ValueError(f'Path is outside {self.path}.')

        if isinstance(v, Mapping):
            d = Directory(p)
            for kk, vv in v.items():
                d[kk] = vv
        elif isinstance(v, (str, bytes)):
            if os.path.exists(p) and not os.path.isfile(p):
                del self[k]
            os.makedirs(os.path.dirname(p), exist_ok=True)
            m = 't' if isinstance(v, str) else 'b'
            with open(p, f'w{m}') as f:
                f.write(v)
        elif isinstance(v, SymLink):
            os.symlink(v.src, p)
        else:
            raise TypeError

    def __delitem__(self, k: _KT) -> None:
        p = os.path.abspath(self.path + os.sep + k)
        if os.path.islink(p) or os.path.isfile(p):
            os.remove(p)
        elif os.path.isdir(p):
            os.rmdir(p)

    def __iter__(self) -> Iterator[str]:
        return iter(os.listdir(self.path))

    def __len__(self) -> int:
        return len(os.listdir(self.path))

    def __str__(self) -> str:
        with os.popen(f'tree --noreport {self.path}', 'r') as p:
            return p.read()


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
        # Ensure platform is linux
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

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

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
        return bool(self.configfs['UDC'].strip())

    @enabled.setter
    def enabled(self, b: bool) -> None:
        if b:
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

        self.configfs[f'functions/{n}'] = function
        self.configfs[f'configs/c.1/{n}'] = SymLink(f'{self.configfs.path}/functions/{n}')

        self._function_count += 1
        return self.configfs[f'functions/{n}']
