from __future__ import annotations

import json
import os
import shutil
import stat

from pathlib import Path
from typing import Dict, Any, Optional

from snapfs.hash import hash_string, hash_file
from snapfs.utilities import (
    path_from_hash,
    make_dirs,
    dict_to_json,
    save_file,
    load_file
)


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

    def serialize(self, **kwargs) -> Dict:
        data: Dict[str, Any] = {}

        return {
            **self._serialize_recursive(self.get_raw()),
            **kwargs
        }

    def get_raw(self) -> Dict:
        return self._data

    def set_raw(self, data: Dict[str, Any]) -> None:
        self._data = data


class Saveable(Serializable):

    def save(self, file_path: Path, **kwargs) -> str:
        data = self.serialize(**kwargs)

        content = dict_to_json(data)

        save_file(file_path, content, **kwargs)

        return str(file_path)

    def load(self, file_path: Path):
        data = self.get_raw()

        data = {
            **data,
            **load_file(file_path)
        }

        self.set_raw(data)


class Blob(Saveable):
    """
    This class represents the data that can be stored as a blob
    """

    def save(self, directory: Path, **kwargs) -> str:
        data = self.serialize(**kwargs)

        content = dict_to_json(data)

        data_hash = hash_string(content)

        file_path = Path(os.path.join(
            directory,
            path_from_hash(data_hash)
        ))

        save_file(file_path, content)

        return data_hash


class File(Blob):
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

    def save(self, directory: Path, **kwargs) -> str:
        data_hash = hash_file(self.path)

        hash_path = Path(os.path.join(
            directory,
            path_from_hash(data_hash)
        ))

        if not hash_path.is_file():
            make_dirs(hash_path.parent)

            shutil.copy(str(self.path), str(hash_path))

            # make file read only
            os.chmod(hash_path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)

        return data_hash


class Directory(Blob):

    def __init__(self) -> None:
        directories: Dict[str, Directory] = {}
        files: Dict[str, File] = {}

        data = {
            "directories": directories,
            "files": files
        }

        super().__init__(**data)

    def save(self, directory: Path, **kwargs) -> str:
        data = {
            "directories": {
                key: value.save(directory, **kwargs)
                for key, value in self.directories.items()
            },
            "files": {
                key: value.save(directory, **kwargs)
                for key, value in self.files.items()
            }
        }

        content = dict_to_json(data)

        data_hash = hash_string(content)

        file_path = Path(os.path.join(
            directory,
            path_from_hash(data_hash)
        ))

        save_file(file_path, content)

        return data_hash


class Author(Serializable):

    def __init__(
        self,
        name: str,
        fullname: Optional[str],
        email: Optional[str]
    ) -> None:
        super().__init__(name=name, fullname=fullname, email=email)


class Commit(Blob):

    def __init__(
        self,
        author: Author,
        message: str,
        previous_commit: Optional[Commit] = None
    ) -> None:
        data = {
            "author": author,
            "message": message,
            "previous_commit": previous_commit
        }

        super().__init__(**data)


class Head(Saveable):

    def __init__(
        self,
        path: Path
    ) -> None:
        super().__init__(path=path, ref=None)

    def serialize(self, **kwargs) -> Dict:
        return {
            "ref": self.ref
        }

    def save(self, **kwargs) -> str:
        return super().save(self.path, **kwargs)

    def load(self):
        return super().load(self.path)


if __name__ == "__main__":
    test_directory = Path(os.path.join(
        os.getcwd(),
        ".data",
        "foo"
    ))

    author = Author(
        "beesperester",
        "Bernhard Esperester",
        "bernhard@esperester.de"
    )

    # print(author.serialize())

    commit = Commit(author, "another commit")

    # print(commit.serialize())

    # commit_id = commit.save(test_directory, tree="foobar")

    tree = Directory()

    tree.files["test"] = File(Path(
        "/Users/bernhardesperester/git/python-snapfs/.data/test/setup-cinema4d/model_main_v145.c4d"
    ))

    # print(tree.serialize())

    # print(tree.save(test_directory))

    head = Head(Path(os.path.join(
        test_directory,
        "HEAD"
    )))

    # head.ref = "branches/main"

    # head.save(override=True)

    head.load()

    print(head.serialize())
