import os
import fnmatch

from pathlib import Path

from typing import List, Optional

from snapfs import fs, transform, file
from snapfs.dataclasses import (
    File,
    Directory,
    Difference,
    FileAddedDifference,
    FileUpdatedDifference,
    FileRemovedDifference
)


def store_tree_as_blob(directory: Path, tree: Directory) -> str:
    data = {
        "directories": {
            key: store_tree_as_blob(directory, value)
            for key, value in tree.directories.items()
        },
        "files": {
            key: file.store_file_as_blob(directory, value)
            for key, value in tree.files.items()
        }
    }

    return fs.save_data_as_blob(directory, data)


def load_blob_as_tree(directory: Path, hashid: str) -> Directory:
    data = fs.load_blob_as_data(directory, hashid)

    data["directories"] = {
        key: load_blob_as_tree(directory, value)
        for key, value in data["directories"].items()
    }

    data["files"] = {
        key: file.load_blob_as_file(directory, value)
        for key, value in data["files"].items()
    }

    return Directory(**data)


def serialize_tree(tree: Directory) -> str:
    data = {
        "directories": {
            key: serialize_tree(value)
            for key, value in tree.directories.items()
        },
        "files": {
            key: file.serialize_file(value)
            for key, value in tree.files.items()
        }
    }

    return transform.string_to_hashid(
        transform.dict_to_json(data)
    )


def glob_filter(string: str, patterns: List[str]) -> bool:
    if not patterns:
        return True

    exclude = [x for x in patterns if not x.startswith("^")]
    include = [x[1:] for x in list(set(patterns) - set(exclude))]

    keep = not any([fnmatch.fnmatch(string, x) for x in exclude])

    if include:
        keep = any([fnmatch.fnmatch(string, x) for x in include])

    return keep


def get_tree(
    current_path: Path,
    patterns: List[str] = []
) -> Directory:
    tree = Directory({}, {})

    # load ignore pattern
    patterns = [
        *patterns,
        *fs.load_ignore_file(current_path)
    ]

    for name in sorted(list(os.listdir(current_path))):
        item_path = Path(os.path.join(current_path, name))

        if item_path.is_file():
            if glob_filter(name, patterns):
                tree.files[name] = File(item_path)
        elif item_path.is_dir():
            result = get_tree(item_path, patterns)

            if result.files or result.directories:
                tree.directories[name] = result

    return tree


def compare_trees(
    a: Directory,
    b: Directory,
    differences: List[Difference] = [],
    path: Optional[Path] = None
) -> None:
    if path is None:
        path = Path()

    for key, value in a.directories.items():
        if key not in b.directories.keys():
            compare_trees(
                value,
                Directory({}, {}),
                differences,
                path.joinpath(key)
            )
        else:
            compare_trees(
                value,
                b.directories[key],
                differences,
                path.joinpath(key)
            )

    # test for added or updated files
    for key, value in a.files.items():
        file_path = path.joinpath(key)

        if key not in b.files.keys():
            differences.append(
                FileAddedDifference(
                    file_path
                )
            )
        elif (
            transform.file_to_hashid(value.path)
            != transform.file_to_hashid(b.files[key].path)
        ):
            differences.append(
                FileUpdatedDifference(
                    file_path
                )
            )

    # test for removed files
    for key, value in b.files.items():
        file_path = path.joinpath(key)

        if key not in a.files.keys():
            differences.append(
                FileRemovedDifference(
                    file_path
                )
            )
