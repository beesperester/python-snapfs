import os
import fnmatch

from pathlib import Path

from typing import Dict, Any, List, Optional, Tuple

from snapfs import fs, transform, file, filters, differences
from snapfs.datatypes import File, Directory, Differences


def store_as_blob(path: Path, directory: Directory) -> str:
    data = {
        "directories": {
            key: store_as_blob(path, value)
            for key, value in directory.directories.items()
        },
        "files": {
            key: file.store_as_blob(path, value)
            for key, value in directory.files.items()
        },
    }

    return fs.store_dict_as_blob(path, data)


def load_from_blob(path: Path, hashid: str) -> Directory:
    data = fs.load_blob_as_dict(path, hashid)

    data["directories"] = {
        key: load_from_blob(path, value)
        for key, value in data["directories"].items()
    }

    data["files"] = {
        key: file.load_from_blob(path, value)
        for key, value in data["files"].items()
    }

    return Directory(**data)


def serialize_as_hashid(directory: Directory) -> str:
    data = {
        "directories": {
            key: serialize_as_hashid(value)
            for key, value in directory.directories.items()
        },
        "files": {
            key: file.serialize_as_hashid(value)
            for key, value in directory.files.items()
        },
    }

    return transform.dict_as_hashid(data)


def serialize_as_dict(directory: Directory) -> Dict[str, Any]:
    return {
        **transform.as_dict(directory),
        "directories": {
            key: serialize_as_dict(value)
            for key, value in directory.directories.items()
        },
        "files": {
            key: file.serialize_as_dict(value)
            for key, value in directory.files.items()
        },
    }


def transform_as_list(path: Path, directory: Directory) -> List[File]:
    files: List[File] = []

    for key, value in directory.directories.items():
        files = files + transform_as_list(path.joinpath(key), value)

    files = files + [
        File(path.joinpath(key), value.is_blob, value.blob_path, value.hashid)
        for key, value in directory.files.items()
    ]

    return files


def transform_from_list(path: Path, paths: List[File]) -> Directory:
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

                result.directories[first_segment] = transform_from_list(
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


def load_from_directory_path(
    current_path: Path, patterns: List[str] = []
) -> Directory:
    directory = Directory({}, {})

    # load ignore pattern
    patterns = [*patterns, *fs.load_ignore_file_as_patterns(current_path)]

    for name in sorted(list(os.listdir(current_path))):
        item_path = Path(os.path.join(current_path, name))

        if item_path.is_file():
            if not filters.ignore(name, patterns):
                directory.files[name] = File(item_path)
        elif item_path.is_dir():
            result = load_from_directory_path(item_path, patterns)

            if result.files or result.directories:
                directory.directories[name] = result

    return directory


def compare(path: Path, old: Directory, new: Directory) -> Differences:
    differences_instance = Differences()

    for key, value in new.directories.items():
        if key not in old.directories.keys():
            differences_instance = differences.merge_differences(
                differences_instance,
                compare(path.joinpath(key), Directory({}, {}), value),
            )
        else:
            differences_instance = differences.merge_differences(
                differences_instance,
                compare(path.joinpath(key), old.directories[key], value),
            )

    # test for added or updated files
    for key, value in new.files.items():
        file_path = path.joinpath(key)

        if key not in old.files.keys():
            differences_instance.added_files.append(File(file_path))
        elif file.serialize_as_hashid(value) != file.serialize_as_hashid(
            old.files[key]
        ):
            differences_instance.updated_files.append(File(file_path))

    # test for removed files
    for key, value in old.files.items():
        file_path = path.joinpath(key)

        if key not in new.files.keys():
            differences_instance.removed_files.append(File(file_path))

    return differences_instance
