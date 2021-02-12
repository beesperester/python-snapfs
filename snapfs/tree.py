import os
import fnmatch

from pathlib import Path

from typing import List, Optional, Tuple

from snapfs import fs, transform, file, filters
from snapfs.datatypes import (
    File,
    Directory,
    Differences,
    FileAddedDifference,
    FileUpdatedDifference,
    FileRemovedDifference,
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
        },
    }

    return fs.store_dict_as_blob(directory, data)


def load_blob_as_tree(directory: Path, hashid: str) -> Directory:
    data = fs.load_blob_as_dict(directory, hashid)

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
            key: file.serialize_file_as_hashid(value)
            for key, value in tree.files.items()
        },
    }

    return transform.string_as_hashid(transform.dict_as_json(data))


def tree_as_list(path: Path, tree: Directory) -> List[File]:
    files: List[File] = []

    for key, value in tree.directories.items():
        files = files + tree_as_list(path.joinpath(key), value)

    files = files + [
        File(path.joinpath(key), True, value.blob_path, value.hashid)
        for key, value in tree.files.items()
    ]

    return files


def list_as_tree(path: Path, paths: List[File]) -> Directory:
    result = Directory()

    for item_instance in paths:
        item_path_relative = item_instance.path.relative_to(path)

        path_parts = item_path_relative.as_posix().split("/")

        if len(path_parts) > 1:
            # recursive lookup
            # add first segment as key for next directory
            first_segment = path_parts[0]

            if first_segment not in result.directories.keys():
                next_path = path.joinpath(first_segment)

                result.directories[first_segment] = list_as_tree(
                    next_path,
                    [
                        x
                        for x in paths
                        if x.path.as_posix().startswith(str(next_path))
                    ],
                )
        else:
            # path_part is file
            result.files[str(item_path_relative)] = item_instance

    return result


def get_tree(current_path: Path, patterns: List[str] = []) -> Directory:
    tree = Directory({}, {})

    # load ignore pattern
    patterns = [*patterns, *fs.load_ignore_file_as_patterns(current_path)]

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


def compare_trees(path: Path, a: Directory, b: Directory) -> Differences:
    differences_instance = Differences()

    for key, value in a.directories.items():
        if key not in b.directories.keys():
            differences_instance = Differences(
                [
                    *differences_instance.differences,
                    *compare_trees(
                        path.joinpath(key), value, Directory({}, {})
                    ).differences,
                ]
            )
        else:
            differences_instance = Differences(
                [
                    *differences_instance.differences,
                    *compare_trees(
                        path.joinpath(key), value, b.directories[key]
                    ).differences,
                ]
            )

    # test for added or updated files
    for key, value in a.files.items():
        file_path = path.joinpath(key)

        if key not in b.files.keys():
            differences_instance.differences.append(
                FileAddedDifference(File(file_path))
            )
        elif transform.file_as_hashid(value.path) != transform.file_as_hashid(
            b.files[key].path
        ):
            differences_instance.differences.append(
                FileUpdatedDifference(File(file_path))
            )

    # test for removed files
    for key, value in b.files.items():
        file_path = path.joinpath(key)

        if key not in a.files.keys():
            differences_instance.differences.append(
                FileRemovedDifference(File(file_path))
            )

    return differences_instance
