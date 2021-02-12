from pathlib import Path
from typing import Any, Dict

from snapfs import fs, transform
from snapfs.datatypes import Head


def store_head_as_file(path: Path, head: Head) -> None:
    fs.store_dict_as_file(path, serialize_head_as_dict(head), override=True)


def load_file_as_head(path: Path) -> Head:
    return Head(**fs.load_file_as_dict(path))


def serialize_head_as_dict(head: Head) -> Dict[str, Any]:
    return transform.as_dict(head)
