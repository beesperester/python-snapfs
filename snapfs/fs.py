import stat
import shutil

from pathlib import Path
from typing import Any, Dict

from snapfs import transform


def make_dirs(path: Path):
    path.mkdir(0o774, True, True)


def save_file(
    file_path: Path,
    content: str,
    override: bool = False
) -> None:
    if file_path.is_file() and override:
        # make file writeable
        file_path.chmod(stat.S_IWRITE | stat.S_IWGRP | stat.S_IROTH)

    if not file_path.is_file() or override:
        make_dirs(file_path.parent)

        with open(file_path, "w") as f:
            f.write(content)

        # make file read only
        file_path.chmod(stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)


def save_data_as_file(
    file_path: Path,
    data: Dict[str, Any],
    override: bool = False
) -> None:
    save_file(file_path, transform.dict_to_json(data), override)


def save_data_as_blob(
    directory: Path,
    data: Dict[str, Any]
) -> str:
    contents = transform.dict_to_json(data)

    hashid = transform.string_to_hashid(contents)

    hashid_path = directory.joinpath(transform.hashid_to_path(hashid))

    save_file(hashid_path, contents)

    return hashid


def load_file(file_path: Path) -> str:
    data: str = ""

    with open(file_path, "r") as f:
        data = f.read()

    return data


def load_file_as_data(file_path: Path) -> Dict[str, Any]:
    return transform.json_to_dict(load_file(file_path))


def load_blob_as_data(directory: Path, hashid: str) -> Dict[str, Any]:
    hashid_path = directory.joinpath(
        transform.hashid_to_path(hashid)
    )

    return load_file_as_data(hashid_path)


def copy_file(source: Path, target: Path) -> None:
    shutil.copyfile(source, target)


def copy_file_as_blob(directory: Path, source: Path) -> str:
    hashid = transform.file_to_hashid(source)

    hashid_path = directory.joinpath(transform.hashid_to_path(hashid))

    if not hashid_path.is_file():
        make_dirs(hashid_path.parent)

        copy_file(source, hashid_path)

        hashid_path.chmod(stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)

    return hashid
