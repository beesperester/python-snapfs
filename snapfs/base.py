import os

from pathlib import Path
from typing import Any, Callable, Dict, Sequence, TypeVar, Union

from snapfs import fs, transform, hash


T = TypeVar("T")


def apply(callback: Callable[[T], Any], values: Sequence[T]) -> None:
    for value in values:
        callback(value)


class Serializable:

    @classmethod
    def serialize_item(cls, item: Any) -> Any:
        if isinstance(item, Serializable):
            return item.get_serialized()
        elif isinstance(item, dict):
            return cls.serialize(item)
        elif isinstance(item, list):
            return [
                cls.serialize_item(x)
                for x in item
            ]

        return item

    @classmethod
    def serialize(cls, data: dict) -> dict:
        data_serialized = {}

        for key, value in data.items():
            data_serialized[key] = cls.serialize_item(value)

        return data_serialized

    def get_serialized(self) -> dict:
        return self.serialize(self.get_dict())

    def get_dict(self) -> dict:
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith("_")
        }

    def set_dict(self, data: dict):
        self.__dict__ = {
            **self.__dict__,
            **data
        }


class Storable(Serializable):

    def __init__(
        self,
        path: Path
    ) -> None:
        self._path = path

    def get_path(self) -> Path:
        return self._path


class Saveable(Storable):

    def save(self, override=False):
        fs.save_file(
            self.get_path(),
            transform.dict_to_json(self.get_serialized()),
            override
        )

        return self


class Loadable(Storable):

    def load(self):
        self.set_dict(
            transform.json_to_dict(fs.load_file(self.get_path()))
        )

        return self


class Head(Saveable, Loadable):

    def __init__(
        self,
        path: Path
    ) -> None:
        self.ref: str = ""

        super().__init__(path)

    def save(self):
        return super().save(override=True)


class Branch(Saveable, Loadable):

    def __init__(
        self,
        path: Path
    ) -> None:
        self.commit_id: str = ""

        super().__init__(path)

    def save(self):
        return super().save(override=True)


class Author(Serializable):

    def __init__(
        self,
        name: str,
        fullname: str = "",
        email: str = ""
    ) -> None:
        self.name = name
        self.fullname = fullname
        self.email = email


class EmptyBlobError(Exception):
    """
    This class represents an empty blob exception
    """


class Blob(Serializable):

    @classmethod
    def save_item(cls, directory: Path, item: Any) -> Any:
        if issubclass(item.__class__, Blob):
            return item.save(directory)
        elif isinstance(item, Serializable):
            return item.get_serialized()
        elif isinstance(item, dict):
            return cls.save_recursive(directory, item)
        elif isinstance(item, list):
            return [
                cls.save_item(directory, x)
                for x in item
            ]

        return item

    @classmethod
    def save_recursive(cls, directory: Path, data: Dict) -> str:
        data_serialized = {}

        for key, value in data.items():
            data_serialized[key] = cls.save_item(directory, value)

        return fs.save_data_as_blob(directory, data_serialized)

    def save(self, directory: Path) -> str:
        return self.save_recursive(directory, self.get_dict())


class File(Blob):

    def __init__(
        self,
        path: Path
    ) -> None:
        if not path.is_file():
            raise ValueError("File '{}' does not exist".format(path))

        self._path = path
        self.size = path.stat().st_size
        self.blob = ""

        super().__init__()

    def save(self, directory: Path) -> str:
        self.blob = hash.hash_file(self._path)

        blob_path = directory.joinpath(transform.hashid_to_path(self.blob))

        fs.make_dirs(blob_path.parent)

        fs.copy_file_as_blob(self._path, blob_path)

        return super().save(directory)


class Directory(Blob):

    def __init__(self) -> None:
        self.directories: Dict[str, Directory] = {}
        self.files: Dict[str, File] = {}
        super().__init__()

    def save(self, directory: Path) -> str:
        if not (self.directories or self.files):
            return ""

        directories_serialized = {}

        for key, value in self.directories.items():
            directories_serialized[key] = value.save(directory)

        files_serialized = {}

        for key, value in self.files.items():
            files_serialized[key] = value.save(directory)

        data_serialized = {
            "directories": directories_serialized,
            "files": files_serialized
        }

        return fs.save_data_as_blob(directory, data_serialized)


class Commit(Blob):

    def __init__(
        self,
        author: Author,
        message: str,
        tree: Directory,
        previous_commit: str = ""
    ) -> None:
        self.author = author
        self.message = message
        self.tree = tree
        self.previous_commit = previous_commit


class CommitBlob(Loadable):

    def __init__(
        self,
        path: Path
    ) -> None:
        super().__init__(path)

    def set_dict(self, data: dict):
        data["author"] = Author(
            **data["author"]
        )

        return super().set_dict(data)


class Repository:

    def __init__(
        self,
        path: Path,
        name: str = ".snapfs"
    ) -> None:
        if not path.is_dir():
            raise ValueError(
                "'{}' must be a valid path on the filesystem".format(
                    path
                )
            )

        self.path = path
        self.name = name
        self.head = Head(self.get_head_path())

        if self.head.get_path().is_file():
            self.head.load()

    def is_initialized(self) -> bool:
        """
        Check if repository is initialized
        """

        paths = [
            self.get_repository_path().is_dir(),
            self.get_blobs_path().is_dir(),
            self.get_branches_path().is_dir(),
            self.get_head_path().is_file()
        ]

        return all(paths)

    def init(self):
        """
        Initialize empty repository
        """

        if self.is_initialized():
            self.head.load()
        else:
            self.create()

    def create(self):
        paths = [
            self.get_repository_path(),
            self.get_blobs_path(),
            self.get_branches_path()
        ]

        # create directories for all paths
        apply(fs.make_dirs, paths)

        # create HEAD file
        self.head.save()

        # create main branch
        self.checkout("main")

    def get_repository_path(self) -> Path:
        return self.path.joinpath(self.name)

    def get_blobs_path(self) -> Path:
        return self.get_repository_path().joinpath("blobs")

    def get_branches_path(self) -> Path:
        return self.get_repository_path().joinpath("branches")

    def get_head_path(self) -> Path:
        return self.get_repository_path().joinpath("HEAD")

    def checkout(self, branch_name: str) -> None:
        branch = Branch(self.get_branches_path().joinpath(branch_name))

        if not branch.get_path().is_file():
            branch.save()

        # update head
        self.set_ref(str(
            branch.get_path().relative_to(self.get_repository_path())
        ))

    def get_ref(self) -> Union[CommitBlob, Branch]:
        if self.head.ref.startswith("branches"):
            return self.get_branch(self.head.ref)
        else:
            return self.get_commit(self.head.ref)

    def get_branch(self, ref: str) -> Branch:
        path = self.get_repository_path().joinpath(ref)

        if not path.is_file():
            raise Exception("Branch '{}' does not exist".format(ref))

        return Branch(path).load()

    def get_commit(self, ref: str) -> CommitBlob:
        path = self.get_blobs_path().joinpath(
            transform.hashid_to_path(ref)
        )

        if not path.is_file():
            raise Exception("CommitBlob '{}' does not exist".format(ref))

        return CommitBlob(path).load()

    def set_ref(self, ref: str) -> None:
        self.head.ref = ref

        self.head.save()

    def get_latest_commit(self) -> CommitBlob:
        ref = self.get_ref()

        if isinstance(ref, Branch):
            return self.get_commit(ref.commit_id)

        return ref

    def snap(self, commit: Commit) -> None:
        commit_id = commit.save(self.get_blobs_path())

        ref = self.get_ref()

        if isinstance(ref, Branch):
            ref.commit_id = commit_id
            ref.save()
        else:
            self.head.ref = commit_id
            self.head.save()


if __name__ == "__main__":
    repository = Repository(Path(os.getcwd()).joinpath(".data/test"))

    repository.init()

    author = Author("beesperester")

    c4d_directory = Directory()
    c4d_directory.files["test.c4d"] = File(Path(
        "/Users/bernhardesperester/git/python-snapfs/.data/test/setup-cinema4d/model_main_v145.c4d"
    ))

    tree = Directory()
    tree.directories["setup-cinema4d"] = c4d_directory

    commit = Commit(author, "initial commit", tree)

    repository.snap(commit)
