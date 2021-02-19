from snapfs.datatypes import (
    Difference,
    FileAddedDifference,
    FileRemovedDifference,
    FileUpdatedDifference,
)


def serialize_difference_as_message(difference: Difference) -> str:
    if isinstance(difference, FileAddedDifference):
        return "added: {}".format(difference.file.path)
    elif isinstance(difference, FileUpdatedDifference):
        return "updated: {}".format(difference.file.path)
    elif isinstance(difference, FileRemovedDifference):
        return "removed: {}".format(difference.file.path)

    raise Exception()