import os

from pathlib import Path
from typing import List, Dict, Optional

from snapfs import head
from snapfs.datatypes import Head


class DirectoryNotFoundError(FileNotFoundError):
    """
    This class represens a directory not found exception
    """


# path helpers
def get_repository_path(path: Path, test: bool = True) -> Path:
    repository_path = path.joinpath(".snapfs")

    if test and not repository_path.is_dir():
        raise DirectoryNotFoundError(repository_path)

    return repository_path


def get_blobs_path(path: Path, test: bool = True) -> Path:
    blobs_path = get_repository_path(path, test).joinpath("blobs")

    if test and not blobs_path.is_dir():
        raise DirectoryNotFoundError(blobs_path)

    return blobs_path


def get_references_path(path: Path, test: bool = True) -> Path:
    references_path = get_repository_path(path, test).joinpath("references")

    if test and not references_path.is_dir():
        raise DirectoryNotFoundError(references_path)

    return references_path


def get_branches_path(path: Path, test: bool = True) -> Path:
    branches_path = get_references_path(path, test).joinpath("branches")

    if test and not branches_path.is_dir():
        raise DirectoryNotFoundError(branches_path)

    return branches_path


def get_tags_path(path: Path, test: bool = True) -> Path:
    tags_path = get_references_path(path, test).joinpath("tags")

    if test and not tags_path.is_dir():
        raise DirectoryNotFoundError(tags_path)

    return tags_path


def get_stage_path(path: Path, test: bool = True) -> Path:
    stage_path = get_repository_path(path, test).joinpath("stage")

    if test and not stage_path.is_file():
        raise FileNotFoundError(stage_path)

    return stage_path


def get_head_path(path: Path, test: bool = True) -> Path:
    head_path = get_repository_path(path, test).joinpath("HEAD")

    if test and not head_path.is_file():
        raise FileNotFoundError(head_path)

    return head_path


def get_head(path: Path) -> Head:
    return head.load_file_as_head(get_head_path(path))
