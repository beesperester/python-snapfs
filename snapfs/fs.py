import stat
import shutil

from pathlib import Path
from typing import Any, Dict, List

from snapfs import transform


def make_dirs(path: Path):
    path.mkdir(0o774, True, True)


def store_file(file_path: Path, content: str, override: bool = False) -> None:
    if file_path.is_file() and override:
        # make file writeable
        file_path.chmod(stat.S_IWRITE | stat.S_IWGRP | stat.S_IROTH)

    if not file_path.is_file() or override:
        make_dirs(file_path.parent)

        with open(file_path, "w") as f:
            f.write(content)

        # make file read only
        file_path.chmod(stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)


def store_dict_as_file(
    file_path: Path, data: Dict[str, Any], override: bool = False
) -> None:
    store_file(file_path, transform.dict_as_json(data), override)


def store_dict_as_blob(directory: Path, data: Dict[str, Any]) -> str:
    contents = transform.dict_as_json(data)

    hashid = transform.string_as_hashid(contents)

    hashid_path = directory.joinpath(transform.hashid_as_path(hashid))

    store_file(hashid_path, contents)

    return hashid


def load_file(file_path: Path) -> str:
    data: str = ""

    with open(file_path, "r") as f:
        data = f.read()

    return data


def load_file_as_dict(file_path: Path) -> Dict[str, Any]:
    return transform.json_as_dict(load_file(file_path))


def load_blob_as_dict(directory: Path, hashid: str) -> Dict[str, Any]:
    hashid_path = directory.joinpath(transform.hashid_as_path(hashid))

    return load_file_as_dict(hashid_path)


def copy_file(source: Path, target: Path) -> None:
    make_dirs(target.parent)

    shutil.copyfile(source, target)


def copy_file_as_blob(directory: Path, source: Path) -> str:
    hashid = transform.file_as_hashid(source)

    hashid_path = directory.joinpath(transform.hashid_as_path(hashid))

    if not hashid_path.is_file():
        make_dirs(hashid_path.parent)

        copy_file(source, hashid_path)

        hashid_path.chmod(stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)

    return hashid


def load_ignore_file_as_patterns(directory: Path) -> List[str]:
    patterns = []

    ignore_file_path = directory.joinpath(".ignore")

    if ignore_file_path.is_file():
        contents = load_file(ignore_file_path)

        patterns = list(
            filter(
                bool,
                [
                    x.strip()
                    for x in contents.split("\n")
                    if not x.startswith("#")
                ],
            )
        )

    return patterns
