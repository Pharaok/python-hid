import os
import shutil
from collections.abc import Iterable, MutableMapping, Iterator, Mapping
from dataclasses import dataclass
from typing import SupportsIndex, Any, Union, Type, TypeVar, Optional

_KT = str
_VT = Union[str, bytes, 'SymLink', 'Directory']
_GT = Mapping[_KT, Union[_VT, '_GT']]  # type: ignore


@dataclass
class SymLink:
    src: str


class Directory(MutableMapping[_KT, _VT]):
    def __init__(self, path: str, m: Optional[_GT] = None) -> None:
        self._path = ''
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
    def path(self, path: str) -> None:
        p = str(os.path.abspath(path))
        if self._path:
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

    def __setitem__(self, k: _KT, v: Union[_VT, _GT]) -> None:
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


ConvertibleToBytes = Union[SupportsIndex, Iterable[SupportsIndex]]


def flatten(it: Iterable[Any], ignore: Union[Type[Any], tuple[Type[Any], ...]] = ()) -> list[Any]:
    flattened = []
    for x in it:
        if isinstance(x, ignore):
            flattened.append(x)
        elif isinstance(x, Iterable):
            flattened.extend(flatten(x, ignore=ignore))
        else:
            flattened.append(x)
    return flattened


_T = TypeVar('_T')


def deep_subclasses(cls: Type[_T]) -> list[Type[_T]]:
    subclasses = cls.__subclasses__()
    for sc in cls.__subclasses__():
        subclasses.extend(deep_subclasses(sc))
    return subclasses
