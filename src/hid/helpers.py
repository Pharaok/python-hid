from collections.abc import Iterable
from math import ceil
from typing import SupportsIndex, Literal, Any, Union, Type, TypeVar

ConvertibleToBytes = Union[SupportsIndex, Iterable[SupportsIndex]]


def int_to_min_bytes(n: SupportsIndex, byteorder: Literal['little', 'big'] = 'little') -> bytes:
    n = int(n)
    min_len = max(1, ceil(n.bit_length() / 8))
    return n.to_bytes(min_len, byteorder)


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


def convert_to_bytes(x: ConvertibleToBytes) -> bytes:
    if isinstance(x, SupportsIndex):
        b = int_to_min_bytes(x)
    else:
        b = bytes(x)
    return b


_T = TypeVar('_T')


def deep_subclasses(cls: Type[_T]) -> list[Type[_T]]:
    subclasses = cls.__subclasses__()
    for sc in cls.__subclasses__():
        subclasses.extend(deep_subclasses(sc))
    return subclasses
