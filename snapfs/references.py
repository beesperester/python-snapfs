import os

from pathlib import Path

from typing import List

from snapfs import fs, transform
from snapfs.datatypes import Branch, Tag


def store_branch_as_file(path: Path, branch: Branch) -> None:
    data = transform.as_dict(branch)

    fs.save_data_as_file(path, data, override=True)


def load_file_as_branch(path: Path) -> Branch:
    return Branch(**fs.load_file_as_data(path))


def store_tag_as_file(path: Path, tag: Tag) -> None:
    data = transform.as_dict(tag)

    fs.save_data_as_file(path, data, override=True)


def load_file_as_tag(path: Path) -> Tag:
    return Tag(**fs.load_file_as_data(path))
