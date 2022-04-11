from __future__ import annotations

import os
import shutil
from collections import defaultdict
from collections.abc import Iterator, Mapping, MutableMapping
from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class SymLink:
    dest: str


_KT = str
_VT = Union['_FileTreeNode', str, SymLink]


class _FileTreeNode(MutableMapping[_KT, _VT]):
    def _factory(self) -> _FileTreeNode:
        return _FileTreeNode(self)

    def __init__(self, parent: Optional[_FileTreeNode] = None,
                 m: Optional[Mapping[_KT, _VT]] = None,
                 k: Optional[_KT] = None
                 ) -> None:
        if parent is not None and k is not None:
            # Modifies parent in-place, since it is a MutableMapping
            # because the parent needs to have a refernce to the
            # child node during initialization in case we need
            # to traverse back to the root node.
            parent._dict[k] = self

        self._dict: defaultdict[_KT, _VT] = defaultdict(self._factory)
        self._parent = parent

        if m is None:
            m = {}
        for k, v in m.items():
            self[k] = v

    def __getitem__(self, k: _KT) -> _VT:
        return self._dict.__getitem__(k)

    def __setitem__(self, k: _KT, v: _VT) -> None:
        if isinstance(v, Mapping):
            _FileTreeNode(self, v, k)
        elif isinstance(v, str | SymLink):
            self._dict[k] = v
            self._bubble_write(k, v)
        else:
            raise TypeError

    def __delitem__(self, k: _KT) -> None:
        return self._dict.__delitem__(k)

    def __iter__(self) -> Iterator[_KT]:
        return self._dict.__iter__()

    def __len__(self) -> int:
        return self._dict.__len__()

    def clear(self) -> None:
        super().clear()
        self._bubble_delete("")

    def setdefault(self, k: _KT, v: Optional[_VT] = None) -> _VT:
        raise NotImplementedError

    def _bubble_write(self, path: str, _v: str | SymLink) -> None:
        # Bubble a value with its path to the root dict
        if self._parent is None:
            raise NotImplemented
        for k, v in self._parent._dict.items():
            if v is self:
                self._parent._bubble_write(f"{k}/{path}", _v)

    def _bubble_delete(self, path: str) -> None:
        # Bubble a path to the root dict
        if self._parent is None:
            raise NotImplemented
        for k, v in self._parent._dict.items():
            if v is self:
                self._parent._bubble_delete(f"{k}/{path}")


class FileTree(_FileTreeNode):
    def __init__(self, path: str, m: Optional[Mapping[_KT, _VT]] = None) -> None:
        self.path = path
        super().__init__(None, m)

    def close(self) -> None:
        print("del", self.path)
        shutil.rmtree(self.path)

    def _bubble_write(self, path: str, _v: str | SymLink):
        p = f"{self.path}/{path}"
        os.makedirs(os.path.dirname(f"{self.path}/{path}"), exist_ok=True)
        if isinstance(_v, SymLink):
            os.symlink(p, _v.dest)
        elif isinstance(_v, str):
            with open(p, "w") as f:
                f.write(_v)

    def _bubble_delete(self, path: str):
        p = f"{self.path}/{path}"
        if os.path.isdir(p):
            shutil.rmtree(f"{self.path}/{path}")
        elif os.path.isfile(p):
            os.remove(p)
