import os
import fnmatch

from pathlib import Path

from typing import List, Optional

from snapfs import fs, transform, file, filters
from snapfs.datatypes import (
    File,
    Directory,
    Differences,
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
            if filters.patterns_filter(name, patterns):
                tree.files[name] = File(item_path)
        elif item_path.is_dir():
            result = get_tree(item_path, patterns)

            if result.files or result.directories:
                tree.directories[name] = result

    return tree


def compare_trees(
    path: Path,
    a: Directory,
    b: Directory
) -> Differences:
    differences_instance = Differences()

    for key, value in a.directories.items():
        if key not in b.directories.keys():
            differences_instance = Differences([
                *differences_instance.differences,
                *compare_trees(
                    path.joinpath(key),
                    value,
                    Directory({}, {})
                ).differences
            ])
        else:
            differences_instance = Differences([
                *differences_instance.differences,
                *compare_trees(
                    path.joinpath(key),
                    value,
                    b.directories[key]
                ).differences
            ])

    # test for added or updated files
    for key, value in a.files.items():
        file_path = path.joinpath(key)

        if key not in b.files.keys():
            differences_instance.differences.append(
                FileAddedDifference(
                    file_path
                )
            )
        elif (
            transform.file_to_hashid(value.path)
            != transform.file_to_hashid(b.files[key].path)
        ):
            differences_instance.differences.append(
                FileUpdatedDifference(
                    file_path
                )
            )

    # test for removed files
    for key, value in b.files.items():
        file_path = path.joinpath(key)

        if key not in a.files.keys():
            differences_instance.differences.append(
                FileRemovedDifference(
                    file_path
                )
            )

    return differences_instance
