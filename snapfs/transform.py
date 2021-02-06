from __future__ import annotations

import json

from typing import Dict, Any
from hashlib import sha256
from pathlib import Path


def dict_to_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def json_to_dict(data: str) -> Dict[str, Any]:
    return json.loads(data)


def hashid_to_path(hashid: str, parts: int = 1, length: int = 2) -> str:
    return "/".join(
        [hashid[i * length:(i * length) + length] for i in range(parts)]
        + [hashid[parts * length:]]
    )


def string_to_hashid(string: str) -> str:
    sha256_hash = sha256()

    sha256_hash.update(string.encode("utf-8"))

    return sha256_hash.hexdigest()


def file_to_hashid(path: Path) -> str:
    assert path.is_file()

    sha256_hash = sha256()

    with open(str(path), "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()