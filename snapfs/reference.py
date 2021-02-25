import os

from pathlib import Path

from typing import Any, Dict, List

from snapfs import fs, transform, branch, tag
from snapfs.datatypes import Branch, Tag, Reference


def serialize_as_dict(reference: Reference) -> Dict[str, Any]:
    if isinstance(reference, Branch):
        return branch.serialize_as_dict(reference)
    elif isinstance(reference, Tag):
        return tag.serialize_as_dict(reference)
    elif isinstance(reference, Reference):
        return transform.as_dict(reference)

    raise Exception(
        "reference must be of type 'Branch' or 'Tag' but is '{}'".format(
            reference.__class__.__name__
        )
    )
