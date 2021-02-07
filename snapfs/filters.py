import fnmatch
from snapfs.datatypes import Differences, Difference

from typing import List


def glob_filter(string: str, patterns: List[str]) -> bool:
    if not patterns:
        return True

    keep = True

    for pattern in patterns:
        if pattern.startswith("^"):
            if fnmatch.fnmatch(string, pattern[1:]):
                keep = True
        else:
            keep = not fnmatch.fnmatch(string, pattern)

    return keep


def filter_differences(
    differences: Differences,
    patterns: List[str]
) -> Differences:
    def filter_difference(difference: Difference) -> bool:
        return not glob_filter(str(difference.path), patterns)

    return Differences(list(
        filter(
            filter_difference,
            differences.differences
        )
    ))
