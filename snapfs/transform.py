from __future__ import annotations

import json
import re

from typing import BinaryIO, Dict, Any, Callable, Sequence, TypeVar
from hashlib import sha256
from pathlib import Path


T = TypeVar("T")


def apply(callback: Callable[[T], Any], values: Sequence[T]) -> None:
    for value in values:
        callback(value)


def as_dict(instance: object) -> Dict[str, Any]:
    return instance.__dict__


def slug(string: str) -> str:
    matches = re.findall(re.compile(r"(\w+)"), string)

    return "".join(list(matches))


def dict_as_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def json_as_dict(data: str) -> Dict[str, Any]:
    return json.loads(data)


def hashid_as_path(hashid: str, parts: int = 1, length: int = 2) -> str:
    return "/".join(
        filter(
            bool,
            [
                hashid[(i * length) : (i * length) + length]
                for i in range(parts)
            ]
            + [hashid[(parts * length) :]],
        )
    )


def string_as_hashid(string: str) -> str:
    sha256_hash = sha256()

    sha256_hash.update(string.encode("utf-8"))

    return sha256_hash.hexdigest()


def dict_as_hashid(data: Dict[str, Any]) -> str:
    return string_as_hashid(dict_as_json(data))


def file_as_hashid(path: Path) -> str:
    sha256_hash = sha256()

    with open(str(path), "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def bytes_as_hashid(buffer: bytes) -> str:
    sha256_hash = sha256()
    sha256_hash.update(buffer)

    return sha256_hash.hexdigest()
