import os

from pathlib import Path

from typing import Any, Dict, List

from snapfs import fs, transform
from snapfs.datatypes import Branch


def store_as_file(path: Path, branch: Branch) -> None:
    fs.store_dict_as_file(
        path, serialize_as_dict(branch), override=True
    )


def load_from_file(path: Path) -> Branch:
    return deserialize_from_dict(fs.load_file_as_dict(path))


def serialize_as_dict(branch: Branch) -> Dict[str, Any]:
    return transform.as_dict(branch)


def deserialize_from_dict(data: Dict[str, Any]) -> Branch:
    return Branch(**data)
