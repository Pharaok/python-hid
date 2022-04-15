from __future__ import annotations

import os
import shutil
from collections.abc import Iterator, MutableMapping
from dataclasses import dataclass
from typing import Mapping, Optional, Union


_KT = str
_VT = Union['Directory', 'SymLink', str, bytes]


@dataclass
class SymLink:
    src: str


@dataclass
class Directory(MutableMapping[_KT, _VT]):
    path: str

    def __init__(self, path, m: Optional[Mapping[_KT, _VT]] = None) -> None:
        if m is None:
            m = {}
        self.path = path
        os.makedirs(self.path, exist_ok=True)

    def __getitem__(self, k: _KT) -> _VT:
        p = self.path + os.sep + k
        if os.path.isfile(p):
            try:
                with open(p, f'rt') as f:
                    return f.read()
            except UnicodeDecodeError:
                with open(p, f'rb') as f:
                    return f.read()
        return Directory(p)

    def __setitem__(self, k: _KT, v: _VT) -> None:
        p = self.path + os.sep + k

        if not self.path.startswith(os.path.abspath(p)):
            raise ValueError
        if os.path.exists(p):
            del self[k]

        if isinstance(v, SymLink):
            os.symlink(v.src, p)
        elif isinstance(v, Mapping):
            d = Directory(p)
            for kk, vv in v.items():
                d[kk] = vv
        else:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            m = 't' if isinstance(v, str) else 'b'
            with open(p, f'w{m}') as f:
                f.write(v)

    def __delitem__(self, k: _KT) -> None:
        p = self.path + os.sep + k
        if os.path.islink(p) or os.path.isfile(p):
            os.remove(p)
        elif os.path.isdir(p):
            shutil.rmtree(p)

    def __iter__(self) -> Iterator[str]:
        return iter(os.listdir(self.path))

    def __len__(self) -> int:
        return len(os.listdir(self.path))

    def __str__(self) -> str:
        with os.popen(f"tree --noreport {self.path}", "r") as p:
            return p.read()
