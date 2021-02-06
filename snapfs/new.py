from __future__ import annotations
import os
import fnmatch

from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, TypeVar, Callable, Any, Sequence, Union

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


@dataclass
class Difference:
    path: Path


@dataclass
class FileAddedDifference(Difference):
    """
    This class represents a file added message
    """


@dataclass
class FileUpdatedDifference(Difference):
    """
    This class represents a file updated message
    """


@dataclass
class FileRemovedDifference(Difference):
    """
    This class represents a file removed message
    """


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

            store_branch_as_file(branch_path, branch)
        else:
            branch = load_file_as_branch(branch_path)

        # update head
        head = Head(str(
            branch_path.relative_to(self.get_repository_path())
        ))

        store_head_as_file(self.get_head_path(), head)

        return branch

    def get_head(self) -> Head:
        return load_file_as_head(self.get_head_path())

    def get_latest_commit_hashid(self) -> str:
        commit_hashid = ""

        try:
            reference = self.get_reference()

            if isinstance(reference, (Branch, Tag)):
                commit_hashid = reference.commit_hashid
        except Exception:
            head = self.get_head()

            commit_hashid = head.ref

        return commit_hashid

    def get_latest_commit(self) -> Commit:
        commit_hashid = self.get_latest_commit_hashid()

        commit_hashid_path = self.get_blobs_path().joinpath(
            transform.hashid_to_path(commit_hashid)
        )

        return load_blob_as_commit(commit_hashid_path)

    def get_reference(self) -> Union[Branch, Tag]:
        head = self.get_head()

        if not head.ref:
            raise Exception("Missing reference")

        if head.ref.startswith("references"):
            if "branches" in head.ref:
                return load_file_as_branch(
                    self.get_repository_path().joinpath(head.ref)
                )
            elif "tags" in head.ref:
                return load_file_as_tag(
                    self.get_repository_path().joinpath(head.ref)
                )

        raise Exception("Reference is commit hashid")

    def get_tags(self) -> List[Tag]:
        return load_tags(self.get_tags_path())

    def get_branches(self) -> List[Branch]:
        return load_branches(self.get_branches_path())

    def commit(self, author: Author, message: str, tree: Directory) -> str:
        head = self.get_head()

        tree_hashid = store_tree_as_blob(self.get_blobs_path(), tree)

        previous_commit_hashid = self.get_latest_commit_hashid()

        commit = Commit(author, message, tree_hashid, previous_commit_hashid)

        commit_hashid = store_commit_as_blob(self.get_blobs_path(), commit)

        try:
            reference = self.get_reference()

            data = {
                **as_dict(reference),
                "commit_hashid": commit_hashid
            }

            if isinstance(reference, Branch):
                branch = Branch(**data)

                store_branch_as_file(
                    self.get_repository_path().joinpath(head.ref),
                    branch
                )
            elif isinstance(reference, Tag):
                # set head to commit hashid
                data = {
                    **as_dict(head),
                    "commit_hashid": commit_hashid
                }

                head = Head(**data)

                store_head_as_file(self.get_head_path(), head)
        except Exception:
            # set head to commit hashid
            data = {
                **as_dict(head),
                "commit_hashid": commit_hashid
            }

            head = Head(**data)

            store_head_as_file(self.get_head_path(), head)

        return commit_hashid


T = TypeVar("T")


def apply(callback: Callable[[T], Any], values: Sequence[T]) -> None:
    for value in values:
        callback(value)


def as_dict(instance: object) -> dict:
    return instance.__dict__


def store_branch_as_file(path: Path, branch: Branch) -> None:
    data = as_dict(branch)

    fs.save_data_as_file(path, data, override=True)


def load_file_as_branch(path: Path) -> Branch:
    return Branch(**fs.load_file_as_data(path))


def load_branches(path: Path) -> List[Branch]:
    return [
        load_file_as_branch(path.joinpath(x)) for x in os.listdir(path)
    ]


def store_tag_as_file(path: Path, tag: Tag) -> None:
    data = as_dict(tag)

    fs.save_data_as_file(path, data, override=True)


def load_file_as_tag(path: Path) -> Tag:
    return Tag(**fs.load_file_as_data(path))


def load_tags(path: Path) -> List[Tag]:
    return [
        load_file_as_tag(path.joinpath(x)) for x in os.listdir(path)
    ]


def store_head_as_file(path: Path, head: Head) -> None:
    data = as_dict(head)

    fs.save_data_as_file(path, data, override=True)


def load_file_as_head(path: Path) -> Head:
    return Head(**fs.load_file_as_data(path))


def store_commit_as_blob(directory: Path, commit: Commit) -> str:
    data = {
        **as_dict(commit),
        "author": as_dict(commit.author)
    }

    return fs.save_data_as_blob(directory, data)


def load_blob_as_commit(path: Path) -> Commit:
    data = fs.load_file_as_data(path)

    data["author"] = Author(**data["author"])

    return Commit(**data)


def store_file_as_blob(directory: Path, file: File) -> str:
    return fs.copy_file_as_blob(directory, file.path)


def load_blob_as_file(directory: Path, hashid: str) -> File:
    hashid_path = directory.joinpath(
        transform.hashid_to_path(hashid)
    )

    return File(hashid_path)


def serialize_file(file: File) -> str:
    return transform.file_to_hashid(file.path)


def store_tree_as_blob(directory: Path, tree: Directory) -> str:
    data = {
        "directories": {
            key: store_tree_as_blob(directory, value)
            for key, value in tree.directories.items()
        },
        "files": {
            key: store_file_as_blob(directory, value)
            for key, value in tree.files.items()
        }
    }

    return fs.save_data_as_blob(directory, data)


def load_blob_as_tree(directory: Path, hashid: str) -> Directory:
    data = fs.load_blob_as_data(directory, hashid)

    data["directories"] = {
        key: load_blob_as_tree(directory, value)
        for key, value in data["directories"].items()
    }

    data["files"] = {
        key: load_blob_as_file(directory, value)
        for key, value in data["files"].items()
    }

    return Directory(**data)


def serialize_tree(tree: Directory) -> str:
    data = {
        "directories": {
            key: serialize_tree(value)
            for key, value in tree.directories.items()
        },
        "files": {
            key: serialize_file(value)
            for key, value in tree.files.items()
        }
    }

    return transform.string_to_hashid(
        transform.dict_to_json(data)
    )


def compare_trees(
    a: Directory,
    b: Directory,
    differences: List[Difference] = [],
    path: Optional[Path] = None
) -> None:
    if path is None:
        path = Path()

    for key, value in a.directories.items():
        if key not in b.directories.keys():
            compare_trees(
                value,
                Directory({}, {}),
                differences,
                path.joinpath(key)
            )
        else:
            compare_trees(
                value,
                b.directories[key],
                differences,
                path.joinpath(key)
            )

    # test for added or updated files
    for key, value in a.files.items():
        file_path = path.joinpath(key)

        if key not in b.files.keys():
            differences.append(
                FileAddedDifference(
                    file_path
                )
            )
        elif (
            transform.file_to_hashid(value.path)
            != transform.file_to_hashid(b.files[key].path)
        ):
            differences.append(
                FileUpdatedDifference(
                    file_path
                )
            )

    # test for removed files
    for key, value in b.files.items():
        file_path = path.joinpath(key)

        if key not in a.files.keys():
            differences.append(
                FileRemovedDifference(
                    file_path
                )
            )


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

    author = Author("beesperester")

    tree = get_tree(Path(os.getcwd()).joinpath(".data/test"), [".snapfs"])

    # repository.commit(author, "initial_commit", tree)

    latest_commit = repository.get_latest_commit()

    latest_tree = load_blob_as_tree(
        repository.get_blobs_path(),
        latest_commit.tree_hashid
    )

    if serialize_tree(tree) != serialize_tree(latest_tree):
        print("compare")
        differences = []

        compare_trees(tree, latest_tree, differences)

        apply(print, differences)
    else:
        print("don't compare")
