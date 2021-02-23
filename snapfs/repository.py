import os

from pathlib import Path
from typing import List, Dict, Optional, Union

from snapfs import head, branch, tag, transform, commit
from snapfs.datatypes import Commit, Head, Tag, Branch, Reference


class DirectoryNotFoundError(FileNotFoundError):
    """
    This class represens a directory not found error
    """


class NoReferenceError(Exception):
    """
    This class represents a no reference error
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


def get_branch_path(path: Path, name: str, test: bool = True) -> Path:
    branch_path = get_branches_path(path, test).joinpath(name)

    if test and not branch_path.is_file():
        raise FileNotFoundError(branch_path)

    return branch_path


def get_tag_path(path: Path, name: str, test: bool = True) -> Path:
    tag_path = get_tags_path(path, test).joinpath(name)

    if test and not tag_path.is_file():
        raise FileNotFoundError(tag_path)

    return tag_path


def get_commit_path(path: Path, commit_hashid: str, test: bool = True) -> Path:
    commit_path = get_blobs_path(path, test).joinpath(
        transform.hashid_as_path(commit_hashid)
    )

    if test and not commit_path.is_file():
        raise FileNotFoundError(commit_path)

    return commit_path


# module helpers
def get_head(path: Path) -> Head:
    return head.load_file_as_head(get_head_path(path))


def get_branch(path: Path, name: str) -> Branch:
    return branch.load_file_as_branch(get_branch_path(path, name))


def get_tag(path: Path, name: str) -> Tag:
    return tag.load_file_as_tag(get_tag_path(path, name))


def get_reference(path: Path) -> Reference:
    head_instance = get_head(path)

    if head_instance.ref:
        if "branches" in head_instance.ref:
            return get_branch(path, Path(head_instance.ref).name)
        if "tags" in head_instance.ref:
            return get_tag(path, Path(head_instance.ref).name)

    raise NoReferenceError("Unable to get reference for '{}'".format(path))


def get_commit(path: Path, commit_hashid: str) -> Commit:
    return commit.load_blob_as_commit(get_commit_path(path, commit_hashid))


def get_latest_commit(path: Path) -> Commit:
    reference_instance = get_reference(path)

    return get_commit(path, reference_instance.commit_hashid)
