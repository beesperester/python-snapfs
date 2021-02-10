from typing import Any, Dict

from snapfs import transform, fs
from snapfs.datatypes import Author, Author


def serialize_author_as_dict(author: Author) -> Dict[str, Any]:
    return transform.as_dict(author)


def deserialize_dict_as_author(data: Dict[str, Any]) -> Author:
    return Author(**data)
