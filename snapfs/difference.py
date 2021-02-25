from typing import Any, Dict

from snapfs import file
from snapfs.datatypes import (
    Difference,
    Differences,
    FileAddedDifference,
    FileRemovedDifference,
    FileUpdatedDifference,
)


def serialize_as_dict(difference: Difference) -> Dict[str, Any]:
    return {
        "type": difference.__class__.__name__,
        "file": file.serialize_as_dict(difference.file),
    }


def deserialize_from_dict(data: Dict[str, Any]) -> Difference:
    difference_type: str = data["type"]

    return globals()[difference_type](
        **{
            **{key: value for key, value in data.items() if key != "type"},
            "file": file.deserialize_from_dict(data["file"]),
        }
    )


def serialize_as_message(difference: Difference) -> str:
    if isinstance(difference, FileAddedDifference):
        return "added: {}".format(difference.file.path)
    elif isinstance(difference, FileUpdatedDifference):
        return "updated: {}".format(difference.file.path)
    elif isinstance(difference, FileRemovedDifference):
        return "removed: {}".format(difference.file.path)

    raise Exception(
        "Difference must be subclass of difference but is '{}'".format(
            difference.__class__.__name__
        )
    )
