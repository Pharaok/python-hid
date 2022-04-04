from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from typing import Generator, Mapping

# Ensure platform is linux
if platform.system() != "Linux":
    raise Exception(f"Unsupported platform: {platform.system()}. Expected linux.")

# Ensure a USB device controller exists
try:
    udc = os.listdir("/sys/class/UDC")[0]
except FileNotFoundError:
    raise Exception("Could not find USB device controller.")

ConfigFS = Mapping[str, 'ConfigFS' | str] # type: ignore

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


@dataclass
class TextFile():
    name: str
    content: str = ""
    path: str = ""


def iter_files(x: ConfigFS) -> Generator[TextFile, None, None]:
    for k, v in x.items():
        if isinstance(v, str):
            yield TextFile(name=k, content=v)
        else:
            dir = iter_files(v)
            for y in dir:
                y.path = f"{k}/{y.path}"
                yield y


def init_configfs(gadget_name: str, fs: ConfigFS) -> None:
    os.makedirs(gadget_name, exist_ok=True)
    os.chdir(gadget_name)
    print(os.curdir)
    for f in iter_files(fs):
        print(f)
        f.path = f"/sys/kernel{f.path}"
        os.makedirs(f.path, exist_ok=True)
        with open(f"{f.path}{f.name}", "w") as file:
            file.write(f.content)
    os.chdir("..")
