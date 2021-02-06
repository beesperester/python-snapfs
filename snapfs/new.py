from __future__ import annotations
import os
import fnmatch

from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, TypeVar, Callable, Any, Sequence, Union

from snapfs import transform, fs


@dataclass
class File:
    path: Path


@dataclass
class Directory:
    directories: Dict[str, Directory]
    files: Dict[str, File]


@dataclass
class Author:
    name: str
    fullname: str = ""
    email: str = ""


@dataclass
class Commit:
    author: Author
    message: str
    tree_hashid: str = ""
    previous_commit_hashid: str = ""


@dataclass
class Head:
    ref: str


@dataclass
class Branch:
    commit_hashid: str = ""


@dataclass
class Tag:
    message: str
    commit_hashid: str = ""


class Repository:

    def __init__(
        self,
        path: Path
    ) -> None:
        self.path = path

        if not self.is_initialized():
            paths = [
                self.get_repository_path(),
                self.get_references_path(),
                self.get_branches_path(),
                self.get_tags_path(),
                self.get_blobs_path()
            ]

            apply(fs.make_dirs, paths)

            self.checkout("main")

    def is_initialized(self) -> bool:
        paths = [
            self.get_repository_path().is_dir(),
            self.get_references_path().is_dir(),
            self.get_branches_path().is_dir(),
            self.get_tags_path().is_dir(),
            self.get_blobs_path().is_dir(),
            self.get_head_path().is_file()
        ]

        return all(paths)

    def get_repository_path(self) -> Path:
        return self.path.joinpath(".snapfs")

    def get_references_path(self) -> Path:
        return self.get_repository_path().joinpath("references")

    def get_branches_path(self) -> Path:
        return self.get_references_path().joinpath("branches")

    def get_tags_path(self) -> Path:
        return self.get_references_path().joinpath("tags")

    def get_blobs_path(self) -> Path:
        return self.get_repository_path().joinpath("blobs")

    def get_head_path(self) -> Path:
        return self.get_repository_path().joinpath("HEAD")

    def get_branch_path(self, name: str) -> Path:
        return self.get_branches_path().joinpath(name)

    def get_tag_path(self, name: str) -> Path:
        return self.get_tags_path().joinpath(name)

    def checkout(self, name: str) -> Branch:
        branch_path = self.get_branch_path(name)

        if not branch_path.is_file():
            commit_hashid = self.get_latest_commit_hashid()

            branch = Branch(commit_hashid)

            store_branch(branch_path, branch)
        else:
            branch = load_branch(branch_path)

        # update head
        head = Head(str(
            branch_path.relative_to(self.get_repository_path())
        ))

        store_head(self.get_head_path(), head)

        return branch

    def get_head(self) -> Head:
        return load_head(self.get_head_path())

    def get_latest_commit_hashid(self) -> str:
        commit_hashid = ""
        head = self.get_head()

        if not head.ref:
            raise Exception("Missing reference")

        if head.ref.startswith("references"):
            if "branches" in head.ref:
                branch = load_branch(
                    self.get_repository_path().joinpath(head.ref)
                )

                commit_hashid = branch.commit_hashid
            elif "tags" in head.ref:
                tag = load_tag(
                    self.get_repository_path().joinpath(head.ref)
                )

                commit_hashid = tag.commit_hashid
        else:
            commit_hashid = head.ref

        return commit_hashid

    def get_reference(self) -> Commit:
        commit_hashid = self.get_latest_commit_hashid()

        commit_hashid_path = self.get_blobs_path().joinpath(
            transform.hashid_to_path(commit_hashid)
        )

        return load_commit(commit_hashid_path)

    def get_tags(self) -> List[Tag]:
        return load_tags(self.get_tags_path())

    def get_branches(self) -> List[Branch]:
        return load_branches(self.get_branches_path())


T = TypeVar("T")


def apply(callback: Callable[[T], Any], values: Sequence[T]) -> None:
    for value in values:
        callback(value)


def as_dict(instance: object) -> dict:
    return instance.__dict__


def store_branch(path: Path, branch: Branch) -> None:
    data = as_dict(branch)

    fs.save_data_as_file(path, data, override=True)


def load_branch(path: Path) -> Branch:
    return Branch(**fs.load_file_as_data(path))


def load_branches(path: Path) -> List[Branch]:
    return [
        load_branch(path.joinpath(x)) for x in os.listdir(path)
    ]


def store_tag(path: Path, tag: Tag) -> None:
    data = as_dict(tag)

    fs.save_data_as_file(path, data, override=True)


def load_tag(path: Path) -> Tag:
    return Tag(**fs.load_file_as_data(path))


def load_tags(path: Path) -> List[Tag]:
    return [
        load_tag(path.joinpath(x)) for x in os.listdir(path)
    ]


def store_head(path: Path, head: Head) -> None:
    data = as_dict(head)

    fs.save_data_as_file(path, data, override=True)


def load_head(path: Path) -> Head:
    return Head(**fs.load_file_as_data(path))


def store_commit(directory: Path, commit: Commit) -> str:
    data = {
        **as_dict(commit),
        "author": as_dict(commit.author)
    }

    return fs.save_data_as_blob(directory, data)


def load_commit(path: Path) -> Commit:
    return Commit(**fs.load_file_as_data(path))


def store_file(directory: Path, file: File) -> str:
    return fs.copy_file_as_blob(directory, file.path)


def store_tree(directory: Path, tree: Directory) -> str:
    data = {
        "directories": {
            key: store_tree(directory, value)
            for key, value in tree.directories.items()
        },
        "files": {
            key: store_file(directory, value)
            for key, value in tree.files.items()
        }
    }

    return fs.save_data_as_blob(directory, data)


def load_ignore_file(directory: Path) -> List[str]:
    patterns = []

    ignore_file_path = directory.joinpath(".ignore")

    if ignore_file_path.is_file():
        contents = fs.load_file(ignore_file_path)

        patterns = list(
            filter(
                bool,
                [
                    x.strip() for x in contents.split("\n")
                    if not x.startswith("#")
                ]
            )
        )

    return patterns


def glob_filter(string: str, patterns: List[str]) -> bool:
    if not patterns:
        return True

    exclude = [x for x in patterns if not x.startswith("^")]
    include = [x[1:] for x in list(set(patterns) - set(exclude))]

    keep = not any([fnmatch.fnmatch(string, x) for x in exclude])

    if include:
        keep = any([fnmatch.fnmatch(string, x) for x in include])

    return keep


def get_tree(
    current_path: Path,
    patterns: List[str] = []
) -> Directory:
    tree = Directory({}, {})

    # load ignore pattern
    patterns = [
        *patterns,
        *load_ignore_file(current_path)
    ]

    for name in sorted(list(os.listdir(current_path))):
        item_path = Path(os.path.join(current_path, name))

        if item_path.is_file():
            if glob_filter(name, patterns):
                tree.files[name] = File(item_path)
        elif item_path.is_dir():
            result = get_tree(item_path, patterns)

            if result.files or result.directories:
                tree.directories[name] = result

    return tree


if __name__ == "__main__":
    test_directory = Path(os.getcwd()).joinpath(".data/test")

    repository = Repository(test_directory)

    repository.checkout("main")

    # author = Author("beesperester")

    # tree = get_tree(Path(os.getcwd()).joinpath(".data/test"), [".snapfs"])

    # tree_hashid = store_tree(test_directory, tree)

    # commit = Commit(author, "initial commit", tree_hashid)

    # commit_hashid = store_commit(test_directory, commit)

    # print(commit_hashid)
