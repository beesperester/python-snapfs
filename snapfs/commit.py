from pathlib import Path

from snapfs import transform, fs
from snapfs.dataclasses import Commit, Author


def store_commit_as_blob(directory: Path, commit: Commit) -> str:
    data = {
        **transform.as_dict(commit),
        "author": transform.as_dict(commit.author)
    }

    return fs.save_data_as_blob(directory, data)


def load_blob_as_commit(path: Path) -> Commit:
    data = fs.load_file_as_data(path)

    data["author"] = Author(**data["author"])

    return Commit(**data)
