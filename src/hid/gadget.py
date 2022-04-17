from __future__ import annotations

import os
import platform
from collections.abc import Iterator, MutableMapping, Sequence
from dataclasses import dataclass
from typing import Mapping, Optional, Union

_KT = str
_VT = Union[str, bytes, 'SymLink', 'Directory']
_GT = Mapping[_KT, _VT | '_GT']  # type: ignore


@dataclass
class SymLink:
    src: str


@dataclass
class Directory(MutableMapping[_KT, _VT]):
    path: str

    def __init__(self, path: str, m: Optional[_GT] = None) -> None:
        self.path = os.path.abspath(path)
        os.makedirs(self.path, exist_ok=True)

        if not m:
            m = {}
        for k, v in m.items():
            self[k] = v

    def __getitem__(self, k: _KT) -> _VT:
        p = os.path.abspath(self.path + os.sep + k)
        if os.path.isfile(p):
            try:
                with open(p, 'rt') as f:
                    return f.read()
            except UnicodeDecodeError:
                with open(p, 'rb') as f:
                    return f.read()
        return Directory(p)

    def __setitem__(self, k: _KT, v: _VT | _GT) -> None:
        p = os.path.abspath(self.path + os.sep + k)

        if not p.startswith(self.path):
            print(p)
            raise ValueError

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
        with os.popen(f"tree --noreport {self.path}", "r") as p:
            return p.read()


class Gadget:
    CONFIGFS = {
        "idVendor": "0x1d6b",
        "idProduct": "0x0104",
        "bcdDevice": "0x0100",
        "bcdUSB": "0x0200",
        "strings": {
            "0x409": {
                "serialnumber": "1234567890",
                "manufacturer": "Pharaok",
                "product": "Pi02"
            }
        },
        "configs": {
            "c.1": {
                "strings": {
                    "0x409": {
                        "configuration": "Config 1: ECM network"
                    }
                },
                "MaxPower": "250"
            }
        }
    }

    def __init__(self,
                 configfs_home: str = "/sys/kernel/config/usb_gadget/",
                 configfs: Optional[_GT] = None,
                 name: str = "hidpy",
                 functions: Optional[Sequence[_GT]] = None) -> None:
        # Ensure platform is linux
        if platform.system() != 'Linux':
            raise Exception(f"Unsupported platform: {platform.system()}. Please use linux.")

        # Ensure a USB device controller exists
        try:
            self.udc = os.listdir("/sys/class/udc")[0]
        except (FileNotFoundError, IndexError):
            raise Exception("Could not find USB device controller.")

        p = f"{configfs_home}/{name}/"
        if os.path.exists(p):
            raise Exception(f"Gadget '{name}' already exists.")

        if configfs is None:
            configfs = self.CONFIGFS
        self.configfs = Directory(p, configfs)
        self._function_count = 0

        if functions is None:
            functions = []
        for f in functions:
            self.add_function(f)

    def __enter__(self) -> Gadget:
        self.enable()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:

        self.disable()

        self.configfs.pop('configs/c.1/strings/0x409')

        for f in self.functions:
            self.configfs.pop(f"configs/c.1/{f}")

        self.configfs.pop('configs/c.1')

        for f in self.functions:
            self.configfs.pop(f"functions/{f}")

        self.configfs.pop('strings/0x409')

        os.rmdir(self.configfs.path)

    def enable(self) -> None:
        self.configfs['UDC'] = self.udc

    def disable(self) -> None:
        self.configfs['UDC'] = ''

    @property
    def functions(self) -> Directory:
        f = self.configfs["functions"]
        if not isinstance(f, Directory):
            raise Exception("'functions' is not a directory.")
        return f

    def add_function(self, function: _GT, name: str = "hid") -> None:
        n = f"{name}.usb{self._function_count}"

        self.configfs[f"functions/{n}"] = function

        self.configfs[f"configs/c.1/{n}"] = SymLink(f"{self.configfs.path}/functions/{n}")
        self._function_count += 1
