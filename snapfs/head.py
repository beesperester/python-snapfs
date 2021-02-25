from pathlib import Path
from typing import Any, Dict

from snapfs import fs, transform
from snapfs.datatypes import Head


def store_as_file(path: Path, head: Head) -> None:
    fs.store_dict_as_file(path, serialize_as_dict(head), override=True)


def load_from_file(path: Path) -> Head:
    return deserialize_from_dict(fs.load_file_as_dict(path))


def serialize_as_dict(head: Head) -> Dict[str, Any]:
    return transform.as_dict(head)


def deserialize_from_dict(data: Dict[str, Any]) -> Head:
    return Head(**data)
