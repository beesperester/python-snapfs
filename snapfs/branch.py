import os

from pathlib import Path

from typing import Any, Dict, List

from snapfs import fs, transform
from snapfs.datatypes import Branch


def store_branch_as_file(path: Path, branch: Branch) -> None:
    fs.store_dict_as_file(
        path, serialize_branch_as_dict(branch), override=True
    )


def load_file_as_branch(path: Path) -> Branch:
    return deserialize_dict_as_branch(fs.load_file_as_dict(path))


def serialize_branch_as_dict(branch: Branch) -> Dict[str, Any]:
    return transform.as_dict(branch)


def deserialize_dict_as_branch(data: Dict[str, Any]) -> Branch:
    return Branch(**data)
