from typing import Any, Dict

from snapfs import file
from snapfs.datatypes import (
    Difference,
    Differences,
    FileAddedDifference,
    FileRemovedDifference,
    FileUpdatedDifference,
)


def serialize_differences_as_dict(differences: Differences) -> Dict[str, Any]:
    return {
        "differences": [
            {
                "type": x.__class__.__name__,
                "file": file.serialize_file_as_dict(x.file),
            }
            for x in differences.differences
        ]
    }


def serialize_difference_as_message(difference: Difference) -> str:
    if isinstance(difference, FileAddedDifference):
        return "added: {}".format(difference.file.path)
    elif isinstance(difference, FileUpdatedDifference):
        return "updated: {}".format(difference.file.path)
    elif isinstance(difference, FileRemovedDifference):
        return "removed: {}".format(difference.file.path)

    raise Exception()