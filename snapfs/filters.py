import fnmatch
from snapfs.datatypes import Differences, Difference

from typing import List


def include_filter(string: str, glob: str) -> bool:
    if glob.startswith("^"):
        return not fnmatch.fnmatch(string, glob[1:])

    return fnmatch.fnmatch(string, glob)


def exclude_filter(string: str, glob: str) -> bool:
    return not include_filter(string, glob)


def patterns_filter(string: str, patterns: List[str]) -> bool:
    if not patterns:
        return True

    keep = True

    for pattern in patterns:
        if not include_filter(string, pattern):
            return True
        else:
            keep = False

    return keep


def filter_differences(
    differences: Differences, patterns: List[str]
) -> Differences:
    def filter_difference(difference: Difference) -> bool:
        return not patterns_filter(str(difference.file.path), patterns)

    return Differences(
        list(filter(filter_difference, differences.differences))
    )


def ignore(string: str, patterns: List[str]) -> bool:
    result = False

    for pattern in patterns:
        if pattern.startswith("^"):
            if fnmatch.fnmatch(string, pattern[1:]):
                result = False
        else:
            if fnmatch.fnmatch(string, pattern):
                result = not result

    return result
