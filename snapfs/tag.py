import os

from pathlib import Path

from typing import Any, Dict, List

from snapfs import fs, transform
from snapfs.datatypes import Tag


def store_as_file(path: Path, tag: Tag) -> None:
    fs.store_dict_as_file(path, serialize_as_dict(tag), override=True)


def load_from_file(path: Path) -> Tag:
    return deserialize_from_dict(fs.load_file_as_dict(path))


def serialize_as_dict(tag: Tag) -> Dict[str, Any]:
    return transform.as_dict(tag)


def deserialize_from_dict(data: Dict[str, Any]) -> Tag:
    return Tag(**data)
