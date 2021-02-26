import fnmatch

from typing import List


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
