from __future__ import annotations

import os
import platform
import shutil
from collections import defaultdict
from collections.abc import Iterator, Mapping, MutableMapping
from typing import Optional, Union

_KT = str
_VT = Union[str, '_FileTree']


class _FileTree(MutableMapping[_KT, _VT]):

    def _factory(self) -> _FileTree:
        return _FileTree(self)

    def __init__(self, parent: Optional[_FileTree] = None, m: Optional[Mapping[_KT, _VT]] = None) -> None:
        self._dict: defaultdict[_KT, _VT] = defaultdict(self._factory)
        self._parent = parent
        if m:
            for k, v in m.items():
                self[k] = v

    def __getitem__(self, k: _KT) -> _VT:
        return self._dict[k]

    def __setitem__(self, k: _KT, v: _VT) -> None:
        if isinstance(v, str):
            self._dict[k] = v
            self._bubble_write(k, v)
        elif isinstance(v, Mapping):
            ft = _FileTree(self)
            for kk, vv in v.items():
                ft[kk] = vv
            self._dict = ft
        else:
            raise TypeError

    def __delitem__(self, k: _KT) -> None:
        self._dict.pop(k)

    def __iter__(self) -> Iterator[_KT]:
        return iter(self._dict)

    def __len__(self) -> int:
        return len(self._dict)

    def clear(self) -> None:
        super().clear()
        self._bubble_delete("")

    def setdefault(self, k: _KT, v: Optional[_VT] = None) -> _VT:
        raise NotImplementedError

    def _bubble_write(self, path: str, _v: str):
        # Bubble a value with its path to the root dict
        if self._parent is None:
            raise Exception('Dangling branch.')
        for k, v in self._parent._dict.items():
            if v is self:
                self._parent._bubble_write(f"{k}/{path}", _v)

    def _bubble_delete(self, path: str):
        # Bubble a path to the root dict
        if self._parent is None:
            raise Exception('Dangling branch.')
        for k, v in self._parent._dict.items():
            if v is self:
                self._parent._bubble_delete(f"{k}/{path}")


class FileTree(_FileTree):
    def __init__(self, path: str, *args, **kwargs) -> None:
        self.path = path
        super().__init__(None, *args, **kwargs)

    def close(self) -> None:
        print("del", self.path)
        shutil.rmtree(self.path)

    def _bubble_write(self, path: str, _v: str):
        os.makedirs(os.path.dirname(f"{self.path}/{path}"), exist_ok=True)
        with open(f"{self.path}/{path}", "w") as f:
            f.write(_v)

    def _bubble_delete(self, path: str):
        p = f"{self.path}/{path}"
        if os.path.isdir(p):
            shutil.rmtree(f"{self.path}/{path}")
        elif os.path.isfile(p):
            os.remove(p)
