from pathlib import Path
from typing import Any, Dict

from snapfs import transform, fs, author
from snapfs.datatypes import Commit, Author


def store_commit_as_blob(directory: Path, commit: Commit) -> str:
    return fs.save_data_as_blob(directory, serialize_commit_as_dict(commit))


def load_blob_as_commit(path: Path) -> Commit:
    data = fs.load_file_as_data(path)

    return deserialize_dict_as_commit(data)


def serialize_commit_as_dict(commit: Commit) -> Dict[str, Any]:
    return {
        **transform.as_dict(commit),
        "author": author.serialize_author_as_dict(commit.author),
    }


def deserialize_dict_as_commit(data: Dict[str, Any]) -> Commit:
    return Commit(
        **{**data, "author": author.deserialize_dict_as_author(data["author"])}
    )
