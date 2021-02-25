from pathlib import Path
from typing import Any, Dict

from snapfs import transform, fs, author
from snapfs.datatypes import Commit, Author


def store_as_blob(directory: Path, commit: Commit) -> str:
    return fs.store_dict_as_blob(directory, serialize_as_dict(commit))


def load_from_blob(path: Path) -> Commit:
    data = fs.load_file_as_dict(path)

    return deserialize_from_dict(data)


def serialize_as_dict(commit: Commit) -> Dict[str, Any]:
    return {
        **transform.as_dict(commit),
        "author": author.serialize_as_dict(commit.author),
    }


def deserialize_from_dict(data: Dict[str, Any]) -> Commit:
    return Commit(
        **{**data, "author": author.deserialize_from_dict(data["author"])}
    )
