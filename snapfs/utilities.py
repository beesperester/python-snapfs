from __future__ import annotations

import json
import os
import re
import stat

from pathlib import Path
from typing import Dict, Any

from snapfs.hash import hash_string


def slug(string: str) -> str:
    matches = re.findall(re.compile(r"(\w+)"), string)

    return "".join(list(matches))


def path_from_hash(hash: str, parts: int = 1, length: int = 2) -> str:
    return "/".join(
        [hash[i * length:(i * length) + length] for i in range(parts)]
        + [hash[parts * length:]]
    )


def make_dirs(path: Path):
    os.makedirs(
        path,
        mode=0o774,
        exist_ok=True
    )


def dict_to_json(data: Dict) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def save_file(file_path: Path, content: str, **kwargs) -> None:
    override = False

    if "override" in kwargs.keys():
        override = bool(kwargs["override"])

    if file_path.is_file() and override:
        # make file writeable
        os.chmod(file_path, stat.S_IWRITE | stat.S_IWGRP | stat.S_IROTH)

    if not file_path.is_file() or override:
        make_dirs(file_path.parent)

        with open(file_path, "w") as f:
            f.write(content)

        # make file read only
        os.chmod(file_path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)


def load_file(file_path: Path) -> Dict[str, Any]:
    data: Dict[str, Any] = {}

    with open(file_path, "r") as f:
        data = {
            **data,
            **json.load(f)
        }

    return data
