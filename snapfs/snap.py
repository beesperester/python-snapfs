from __future__ import annotations

import json
import os
import stat
import re
import shutil
import fnmatch

from typing import Any, Dict, List, Optional, NewType, Tuple, Union
from pathlib import Path

from snapfs.config import config
from snapfs.hash import hash_file, hash_string


class Repository:

    def __init__(
        self,
        root_path: Path
    ) -> None:
        if not root_path.is_dir():
            raise NotADirectoryError(root_path)

        self._root_path = root_path

    def is_initialized(self) -> bool:
        # check container directory
        if not self.get_container_path().is_dir():
            # raise NotADirectoryError(self.GetContainerPath())
            return False

        if not self.get_blobs_path().is_dir():
            return False

        if not self.get_branches_path().is_dir():
            return False

        if not self.get_head_path().is_file():
            return False

        return True

    def init(self):
        # create container directory
        make_dirs(self.get_container_path())

        # create blobs diretory
        make_dirs(self.get_blobs_path())

        # create branches directory
        make_dirs(self.get_branches_path())

        # create main branch
        main_branch_path = self.create_branch("main")

        # set head
        self.set_head(main_branch_path.relative_to(self.get_container_path()))

    def get_container_path(self) -> Path:
        return Path(os.path.join(
            self.get_root_path(),
            ".snapfs"
        ))

    def get_blobs_path(self) -> Path:
        return Path(os.path.join(
            self.get_container_path(),
            "blobs"
        ))

    def get_branches_path(self) -> Path:
        return Path(os.path.join(
            self.get_container_path(),
            "branches"
        ))

    def get_root_path(self) -> Path:
        return self._root_path

    def get_head_path(self) -> Path:
        return Path(os.path.join(
            self.get_container_path(),
            "HEAD"
        ))

    def create_branch(self, name: str) -> Path:
        branch_path = Path(os.path.join(
            self.get_branches_path(),
            name
        ))

        if not branch_path.is_file():
            branch_data = {
                "commit": None
            }

            branch_string = dict_as_string(branch_data)

            with open(branch_path, "w") as f:
                f.write(branch_string)

        return branch_path

    def set_head(self, ref: Path) -> Path:
        head_path = Path(os.path.join(
            self.get_container_path(),
            "HEAD"
        ))

        content = {
            "ref": str(ref)
        }

        content_string = dict_as_string(content)

        with open(head_path, "w") as f:
            f.write(content_string)

        return head_path

    def get_head(self) -> Path:
        content_string = ""

        head_path = Path(os.path.join(
            self.get_container_path(),
            "HEAD"
        ))

        head_data = {}

        with open(head_path, "r") as f:
            head_data = json.load(f)

        ref_path = Path(os.path.join(
            self.get_container_path(),
            head_data["ref"]
        ))

        return ref_path

    def snap(self, commit: Commit, tree: Directory) -> str:
        # store tree
        tree_hash = self.store_tree(tree)

        # store commit
        commit_data = commit.serialize(tree=tree_hash)

        commit_string = dict_as_string(commit_data)

        commit_hash = string_to_blob(commit_string, self.get_blobs_path())

        ref_path = self.get_head()

        if ref_path.is_file():
            if str(ref_path.relative_to(
                self.get_container_path()
            )).startswith("branches"):
                with open(ref_path, "w") as f:
                    branch_content = {
                        "commit": commit_hash
                    }
                    f.write(dict_as_string(branch_content))

        return commit_hash

    def store_tree(self, directory: Directory) -> str:
        content = {
            "directories": {},
            "files": {}
        }

        for name, subdirectory in directory.directories.items():
            content["directories"][name] = self.store_tree(subdirectory)

        for name, file in directory.files.items():
            content["files"][name] = file_to_blob(file, self.get_blobs_path())

        content_string = dict_as_string(content)

        return string_to_blob(content_string, self.get_blobs_path())


def make_dirs(path: Path):
    os.makedirs(
        path,
        mode=0o774,
        exist_ok=True
    )


def string_to_blob(content: str, blobs_path: Path) -> str:
    content_hash = hash_string(content)

    blob_hash_path = Path(os.path.join(
        blobs_path,
        split_string(content_hash)
    ))

    if not blob_hash_path.is_file():
        make_dirs(blob_hash_path.parent)

        with open(blob_hash_path, "w") as f:
            f.write(content)

        # make file read only
        os.chmod(blob_hash_path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)

    return content_hash


def file_to_blob(file: File, blobs_path: Path) -> str:
    file_hash = file.get_hash()

    file_hash_path = Path(os.path.join(
        blobs_path,
        split_string(file_hash)
    ))

    if not file_hash_path.is_file():
        make_dirs(file_hash_path.parent)

        shutil.copy(str(file.path), str(file_hash_path))

        # make file read only
        os.chmod(file_hash_path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)

    return file_hash


def dict_as_string(data: Dict) -> str:
    return json.dumps(data, indent=2)


class Blob:

    def serialize(self, **kwargs: Dict) -> Dict:
        return kwargs


class Commit(Blob):

    def __init__(
        self,
        author: Author,
        message: str,
        previous_commit: Optional[str] = None
    ) -> None:
        self.author = author
        self.message = message
        self.previous_commit = previous_commit

    def serialize(self, **kwargs) -> Dict:
        return super().serialize(**{
            "author": self.author.serialize(),
            "message": self.message,
            "previous_commit": self.previous_commit,
            **kwargs
        })


class Author(Blob):

    def __init__(
        self,
        name: str,
        fullname: Optional[str],
        email: Optional[str]
    ) -> None:
        self.name = name
        self.fullname = fullname
        self.email = email

    def serialize(self, **kwargs) -> Dict:
        data = {
            "name": self.name
        }

        if self.fullname:
            data["fullname"] = self.fullname

        if self.email:
            data["email"] = self.email

        return super().serialize(**{
            **data,
            **kwargs
        })


def slug(string: str) -> str:
    matches = re.findall(re.compile(r"(\w+)"), string)

    return "".join(list(matches))


def glob_filter(string: str) -> bool:
    exclude = [x for x in config.ignore if not x.startswith("^")]
    include = [x[1:] for x in list(set(config.ignore) - set(exclude))]

    keep = not any([fnmatch.fnmatch(string, x) for x in exclude])

    if include:
        keep = any([fnmatch.fnmatch(string, x) for x in include])

    return keep


class File(Blob):
    """
    This class represents a file
    """

    def __init__(
        self,
        path: Path
    ) -> None:
        self.path = path

    def get_hash(self) -> str:
        return hash_file(self.path)


class Directory(Blob):
    """
    This class represents a directory
    """

    def __init__(self) -> None:
        self.files: Dict[str, File] = {}
        self.directories: Dict[str, Directory] = {}


def get_files(current_path: Path, root: Optional[Path] = None) -> Directory:
    tree = Directory()

    for name in sorted(list(os.listdir(current_path))):
        item_path = Path(os.path.join(current_path, name))

        if item_path.is_file():
            relative_item_path = name

            if root:
                item_path.relative_to(root)

            if glob_filter(name):
                tree.files[name] = File(item_path)
        elif item_path.is_dir():
            result = get_files(item_path, current_path)

            if result.files or result.directories:
                tree.directories[name] = result

    return tree


def split_string(string: str, parts: int = 1, length: int = 2) -> str:
    return "/".join(
        [string[i * length:(i * length) + length] for i in range(parts)]
        + [string[parts * length:]]
    )


if __name__ == "__main__":
    test_directory = Path(os.path.join(
        os.getcwd(),
        ".data/test"
    ))

    repository = Repository(test_directory)

    if not repository.is_initialized():
        repository.init()

    tree = get_files(repository.get_root_path())

    author = Author(
        "beesperester",
        "Bernhard Esperester",
        "bernhard@esperester.de"
    )

    commit = Commit(author, "initial commit")

    print(repository.snap(commit, tree))
