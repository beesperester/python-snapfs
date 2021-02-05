from __future__ import annotations

import json
import os
import shutil
from snapfs.snap import make_dirs
import stat

from pathlib import Path
from typing import Dict, Any, Optional

from snapfs.hash import hash_string, hash_file
from snapfs import utilities


class Serializable:

    def __init__(self, **kwargs) -> None:
        self.__dict__["_data"] = kwargs

    def __getattr__(self, name):
        if name in self.__dict__["_data"].keys():
            return self.__dict__["_data"][name]

        raise AttributeError("{} has no attribute '{}'".format(
            self.__class__.__name__,
            name
        ))

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.__dict__["_data"].keys():
            self.__dict__["_data"][name] = value
        else:
            super().__setattr__(name, value)

    @classmethod
    def _serialize_recursive(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        data_serialized: Dict[str, Any] = {}

        for key, value in data.items():
            if isinstance(value, dict):
                value = cls._serialize_recursive(value)
            elif isinstance(value, Serializable):
                value = value.serialize()
            elif isinstance(value, Path):
                value = str(value)

            data_serialized[key] = value

        return data_serialized

    def serialize(self) -> Dict[str, Any]:
        return self._serialize_recursive(self.get_raw())

    def get_raw(self) -> Dict[str, Any]:
        return self._data

    def set_raw(self, data: Dict[str, Any]) -> None:
        self._data = data


class IStorable:
    """
    This class represents the data that can be stored
    """

    def save(self, *args) -> str:
        raise NotImplementedError("{} must implement 'save'".format(
            self.__class__.__name__
        ))

    def load(self, *args) -> None:
        raise NotImplementedError("{} must implement 'load'".format(
            self.__class__.__name__
        ))


class IBlob(IStorable):
    """
    This class represents the data that can be stored as blob
    """

    def save(self, directory: Path) -> str:
        raise NotImplementedError("{} must implement 'save'".format(
            self.__class__.__name__
        ))

    def load(self, directory: Path) -> None:
        raise NotImplementedError("{} must implement 'load'".format(
            self.__class__.__name__
        ))


class File(IBlob, Serializable):
    """
    This class represents a file
    """

    def __init__(
        self,
        path: Path
    ) -> None:
        data = {
            "path": path
        }

        super().__init__(**data)

    def save(self, directory: Path) -> str:
        data_hash = hash_file(self.path)

        hash_path = Path(os.path.join(
            directory,
            utilities.path_from_hash(data_hash)
        ))

        if not hash_path.is_file():
            utilities.make_dirs(hash_path.parent)

            shutil.copy(str(self.path), str(hash_path))

            # make file read only
            os.chmod(hash_path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)

        return data_hash

    def load(self, directory: Path, file_id: str) -> None:
        pass


class Directory(IBlob, Serializable):

    def __init__(self) -> None:
        directories: Dict[str, Directory] = {}
        files: Dict[str, File] = {}

        data = {
            "directories": directories,
            "files": files
        }

        super().__init__(**data)

    def save(self, directory: Path) -> str:
        data = {
            "directories": {
                key: value.save(directory)
                for key, value in self.directories.items()
            },
            "files": {
                key: value.save(directory)
                for key, value in self.files.items()
            }
        }

        content = utilities.dict_to_json(data)

        data_hash = hash_string(content)

        file_path = Path(os.path.join(
            directory,
            utilities.path_from_hash(data_hash)
        ))

        utilities.save_file(file_path, content)

        return data_hash

    def load(self, directory: Path, tree_id: str) -> None:
        data = self.get_raw()

        file_path = Path(os.path.join(
            directory,
            utilities.path_from_hash(tree_id)
        ))

        data = {
            **utilities.load_file(file_path)
        }

        for key, value in data["directories"].items():
            if isinstance(value, str):
                directory_item = Directory()

                directory_item.load(
                    directory,
                    value
                )

                data["directories"][key] = directory_item

        for key, value in data["files"].items():
            if isinstance(value, str):
                file_path = Path(os.path.join(
                    directory,
                    utilities.path_from_hash(value)
                ))

                file_item = File(file_path)

                data["files"][key] = file_item

        self.set_raw(data)


class Author(Serializable):

    def __init__(
        self,
        name: str,
        fullname: Optional[str],
        email: Optional[str]
    ) -> None:
        super().__init__(name=name, fullname=fullname, email=email)


class Commit(IBlob, Serializable):

    def __init__(
        self,
        author: Author,
        message: str,
        previous_commit: Optional[Commit] = None,
        tree_id: Optional[str] = None
    ) -> None:
        data = {
            "author": author,
            "message": message,
            "previous_commit": previous_commit,
            "tree_id": tree_id
        }

        super().__init__(**data)

    def save(self, directory: Path) -> str:
        data = self.serialize()

        content = utilities.dict_to_json(data)

        commit_id = hash_string(content)

        file_path = Path(os.path.join(
            directory,
            utilities.path_from_hash(commit_id)
        ))

        utilities.save_file(file_path, content)

        return commit_id

    def load(self, directory: Path, commit_id: str) -> None:
        data = self.get_raw()

        file_path = Path(os.path.join(
            directory,
            utilities.path_from_hash(commit_id)
        ))

        data = {
            **data,
            **utilities.load_file(file_path)
        }

        if "author" in data.keys():
            data["author"] = Author(
                utilities.default(lambda: data["author"]["name"], ""),
                utilities.default(lambda: data["author"]["fullname"], None),
                utilities.default(lambda: data["author"]["email"], None)
            )

        self.set_raw(data)


class Head(IStorable, Serializable):

    def __init__(
        self,
        path: Path
    ) -> None:
        super().__init__(path=path, ref=None)

    def serialize(self) -> Dict:
        return {
            "ref": self.ref
        }

    def save(self) -> str:
        data = self.serialize()

        content = utilities.dict_to_json(data)

        utilities.save_file(self.path, content, override=True)

        return str(self.path)

    def load(self):
        data = self.get_raw()

        data = {
            **data,
            **utilities.load_file(self.path)
        }

        self.set_raw(data)


class Repository:

    def __init__(
        self,
        path: Path
    ) -> None:
        self.path = path

        self.head = Head(self.get_head_path())

        if not self.is_initialized():
            self.initialize()

    def is_initialized(self):
        # check paths
        return all([
            self.get_container_path().is_dir(),
            self.get_blobs_path().is_dir(),
            self.get_branches_path().is_dir(),
            self.get_head_path().is_file()
        ])

    def initialize(self):
        make_dirs(self.get_container_path())

        make_dirs(self.get_blobs_path())

        make_dirs(self.get_branches_path())

        self.head.save()

    def get_container_path(self) -> Path:
        return self.path.joinpath(".snapfs")

    def get_blobs_path(self) -> Path:
        return self.get_container_path().joinpath("blobs")

    def get_branches_path(self) -> Path:
        return self.get_container_path().joinpath("branches")

    def get_head_path(self) -> Path:
        return self.get_container_path().joinpath("HEAD")


if __name__ == "__main__":
    test_directory = Path(os.path.join(
        os.getcwd(),
        ".data",
        "test"
    ))

    author = Author(
        "beesperester",
        "Bernhard Esperester",
        "bernhard@esperester.de"
    )

    repository = Repository(test_directory)

    commit = Commit(author, "another commit")

    tree = utilities.get_tree(test_directory)
