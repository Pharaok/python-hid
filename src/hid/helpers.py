from collections.abc import Iterable
from math import ceil
from typing import SupportsIndex, Literal, Any, Union

ConvertibleToBytes = Union[SupportsIndex, Iterable[SupportsIndex]]


def int_to_min_bytes(n: SupportsIndex, byteorder: Literal['little', 'big'] = 'little') -> bytes:
    n = int(n)
    min_len = max(1, ceil(n.bit_length() / 8))
    return n.to_bytes(min_len, byteorder)


def flatten(it: Iterable[Any]) -> list[Any]:
    flattened = []
    for x in it:
        if isinstance(x, Iterable):
            flattened.extend(flatten(x))
        else:
            flattened.append(x)
    return flattened


def convert_to_bytes(x: ConvertibleToBytes) -> bytes:
    if isinstance(x, SupportsIndex):
        b = int_to_min_bytes(x)
    else:
        b = bytes(x)
    return b
