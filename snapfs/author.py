from typing import Any, Dict

from snapfs import transform, fs
from snapfs.datatypes import Author, Author


def serialize_as_dict(author: Author) -> Dict[str, Any]:
    return transform.as_dict(author)


def deserialize_from_dict(data: Dict[str, Any]) -> Author:
    return Author(**data)
