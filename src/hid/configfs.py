from __future__ import annotations

import os
import platform
from collections import defaultdict
from typing import Mapping, Optional

# Ensure platform is linux
if platform.system() != 'Linux':
    raise Exception(f"Unsupported platform: {platform.system()}. Expected linux.")

# Ensure a USB device controller exists
try:
    udc = os.listdir("/sys/class/UDC")[0]
except FileNotFoundError:
    raise Exception("Could not find USB device controller.")

fs = {
    "idVendor": "0x1d6b",
    "idProduct": "0x0104",
    "bcdDevice": "0x0100",
    "bcdUSB": "0x0200",
    "UDC": "",
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
                    "configuration": "Config 1"
                }
            },
            "MaxPower": "250"
        }
    }
}


class _FileTree:
    def _factory(self) -> _FileTree:
        return _FileTree(self)

    def __init__(self, parent: Optional[_FileTree] = None, m: Optional[Mapping] = None) -> None:
        self._dict = defaultdict(self._factory)
        self._parent = parent
        if m:
            for k, v in m.items():
                self[k] = v

    def __getitem__(self, k: str) -> _FileTree | str:
        return self._dict[k]

    def __setitem__(self, k: str, v: _FileTree | str) -> None:
        if isinstance(v, str):
            self._dict[k] = v
            self._bubble(k, v)
        elif isinstance(v, Mapping):
            self._dict[k] = _FileTree(self)
            for kk, vv in v.items():
                self._dict[k][kk] = vv
        else:
            raise TypeError

    def _bubble(self, path: str, _v: str):
        for k, v in self._parent._dict.items():
            if v is self:
                self._parent._bubble(f"{k}/{path}", _v)


class FileTree(_FileTree):
    def __init__(self, path: str, *args, **kwargs) -> None:
        self.path = path
        super().__init__(None, *args, **kwargs)

    def _bubble(self, path: str, _v: str):
        os.makedirs(os.path.dirname(f"{self.path}/{path}"), exist_ok=True)
        with open(f"{self.path}/{path}", "w") as f:
            f.write(_v)
