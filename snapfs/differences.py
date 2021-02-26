from pathlib import Path
from typing import Any, Dict, List

from snapfs import file, transform, fs
from snapfs.datatypes import Differences


def store_as_file(path: Path, differences: Differences) -> None:
    fs.store_dict_as_file(path, serialize_as_dict(differences), override=True)


def serialize_as_dict(differences: Differences) -> Dict[str, Any]:
    data = transform.as_dict(differences)

    return {
        **data,
        "added_files": [
            file.serialize_as_dict(x) for x in differences.added_files
        ],
        "updated_files": [
            file.serialize_as_dict(x) for x in differences.updated_files
        ],
        "removed_files": [
            file.serialize_as_dict(x) for x in differences.removed_files
        ],
    }


def deserialize_from_dict(data: Dict[str, Any]) -> Differences:
    return Differences(
        **{
            **data,
            "added_files": [
                file.deserialize_from_dict(x) for x in data["added_files"]
            ],
            "updated_files": [
                file.deserialize_from_dict(x) for x in data["updated_files"]
            ],
            "removed_files": [
                file.deserialize_from_dict(x) for x in data["removed_files"]
            ],
        }
    )


def load_from_file(path: Path) -> Differences:
    return deserialize_from_dict(fs.load_file_as_dict(path))


def merge_differences(a: Differences, b: Differences) -> Differences:
    return Differences(
        [*a.added_files, *b.added_files],
        [*a.updated_files, *b.updated_files],
        [*a.removed_files, *b.removed_files],
    )


def serialize_as_messages(differences: Differences) -> List[str]:
    messages: List[str] = [
        *["added: {}".format(x.path) for x in differences.added_files],
        *["updated: {}".format(x.path) for x in differences.updated_files],
        *["removed: {}".format(x.path) for x in differences.removed_files],
    ]

    return messages
