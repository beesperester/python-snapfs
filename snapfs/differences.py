from typing import Any, Dict

from snapfs import file, difference
from snapfs.datatypes import (
    Difference,
    Differences,
    FileAddedDifference,
    FileRemovedDifference,
    FileUpdatedDifference,
)


def serialize_as_dict(differences: Differences) -> Dict[str, Any]:
    return {
        "differences": [
            difference.serialize_as_dict(x)
            for x in differences.differences
        ]
    }


def deserialize_from_dict(data: Dict[str, Any]) -> Differences:
    return Differences(
        **{
            **data,
            "differences": [
                difference.deserialize_from_dict(x)
                for x in data["differences"]
            ],
        }
    )
