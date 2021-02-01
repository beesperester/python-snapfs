import os
import fnmatch

from pathlib import Path
from typing import List

from snapfs import hash
from snapfs.hash import hash_file, hash_directory
from snapfs.config import config


class Diffmessage:
    """
    This class represents a diff message
    """

    def __init__(self, a: Path, b: Path) -> None:
        self._a = a
        self._b = b

    def get_a(self) -> Path:
        return self._a

    def get_b(self) -> Path:
        return self._b

    def get_message(self):
        raise NotImplementedError

    def action(self):
        raise NotImplementedError


class DiffMissingItemMessage(Diffmessage):
    """
    This class represents a missing item message
    """

    def get_message(self):
        return "'{}' is missing in '{}'".format(
            self.get_a(),
            self.get_b()
        )


class DiffExtraItemMessage(Diffmessage):
    """
    This class represents an extra item message
    """

    def get_message(self):
        return "'{}' is present in '{}' but should not".format(
            self.get_a(),
            self.get_b()
        )


class DiffItemShouldBeFileMessage(Diffmessage):
    """
    This class represents an item should be file message
    """

    def get_message(self):
        return "'{}' is a file but '{}' is not".format(
            self.get_a(),
            self.get_b()
        )


class DiffFileContentsMessage(Diffmessage):
    """
    This class represents a file contents message
    """

    def get_message(self):
        return "'{}' is different in contents as '{}'".format(
            self.get_a(),
            self.get_b()
        )


class DiffItemShouldBeDirectoryMessage(Diffmessage):
    """
    This class represents an item should be directory message
    """

    def get_message(self):
        return "'{}' is a directory but '{}' is not".format(
            self.get_a(),
            self.get_b()
        )


class DiffDirectoryContentsMessage(Diffmessage):
    """
    This class represents a directory contents message
    """

    def get_message(self):
        return "'{}' is different in contents as '{}'".format(
            self.get_a(),
            self.get_b()
        )


class Diffbag(list):
    """
    This class represents a bag full of diff messages and actions
    """


def diff_files(a: Path, b: Path) -> bool:
    return hash_file(a) == hash_file(b)


def glob_filter(string: str) -> bool:
    return not any([fnmatch.fnmatch(string, x) for x in config.ignore])


def diff_directories(a: Path, b: Path, diffbag: Diffbag) -> bool:
    assert a.is_dir()
    assert b.is_dir()

    is_equal = True

    a_items = sorted(list(filter(glob_filter, os.listdir(a))))
    b_items = sorted(list(filter(glob_filter, os.listdir(b))))

    for name in a_items:
        a_item_path = Path(os.path.join(a, name))
        b_item_path = Path(os.path.join(b, name))

        if not b_item_path.exists():
            diffbag.append(DiffMissingItemMessage(
                a_item_path,
                b
            ))

            is_equal = False
        else:
            if a_item_path.is_file() and not b_item_path.is_file():
                diffbag.append(DiffItemShouldBeFileMessage(
                    a_item_path,
                    b_item_path
                ))

                is_equal = False
            elif a_item_path.is_file() and b_item_path.is_file():
                if not diff_files(a_item_path, b_item_path):
                    diffbag.append(DiffFileContentsMessage(
                        a_item_path,
                        b_item_path
                    ))

                    is_equal = False
                else:
                    pass
            elif a_item_path.is_dir() and not b_item_path.is_dir():
                diffbag.append(DiffItemShouldBeDirectoryMessage(
                    a_item_path,
                    b_item_path
                ))

                is_equal = False
            elif a_item_path.is_dir() and b_item_path.is_dir():
                if not diff_directories(a_item_path, b_item_path, diffbag):
                    diffbag.append(DiffDirectoryContentsMessage(
                        a_item_path,
                        b_item_path
                    ))

                    is_equal = False
                else:
                    pass

    for name in b_items:
        # check for paths that are present in b and not in a
        # and should be removed
        a_item_path = Path(os.path.join(a, name))
        b_item_path = Path(os.path.join(b, name))

        if not a_item_path.exists():
            diffbag.append(DiffExtraItemMessage(
                b_item_path,
                a
            ))

    return is_equal


if __name__ == "__main__":
    diffbag = Diffbag()

    print(diff_directories(
        Path(os.path.join(os.getcwd(), ".data/new")),
        Path(os.path.join(os.getcwd(), ".data/base")),
        diffbag
    ))

    for message in diffbag:
        print(message.get_message())
